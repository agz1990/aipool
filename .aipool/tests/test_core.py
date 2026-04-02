#!/usr/bin/env python3
"""
AIPool 单元测试
测试 builtin 操作、adapter 解析、状态管理
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# 添加 lib 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))


class TestBuiltinOps(unittest.TestCase):
    """测试 builtin 操作库"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_mkdir_local(self):
        from builtin_ops import run_builtin
        target = os.path.join(self.tmp, "a/b/c")
        result = run_builtin("mkdir", {"paths": [target], "mode": "755"}, None)
        self.assertTrue(os.path.isdir(target))
        self.assertIn("已创建目录", result)

    def test_check_os_pass(self):
        from builtin_ops import run_builtin
        import platform
        current = platform.system().lower()
        result = run_builtin("check_os", {"allowed": [current]}, None)
        self.assertIn("通过", result)

    def test_check_os_fail(self):
        from builtin_ops import run_builtin, BuiltinError
        with self.assertRaises(BuiltinError):
            run_builtin("check_os", {"allowed": ["nonexistent_os"]}, None)

    def test_check_disk_pass(self):
        from builtin_ops import run_builtin
        result = run_builtin("check_disk", {"path": "/", "min_gb": 1}, None)
        self.assertIn("通过", result)

    def test_check_disk_fail(self):
        from builtin_ops import run_builtin, BuiltinError
        with self.assertRaises(BuiltinError):
            run_builtin("check_disk", {"path": "/", "min_gb": 999999}, None)

    def test_unknown_action(self):
        from builtin_ops import run_builtin, BuiltinError
        with self.assertRaises(BuiltinError):
            run_builtin("nonexistent_action", {}, None)

    def test_compute_local_hash(self):
        from builtin_ops import compute_local_file_hash
        f = os.path.join(self.tmp, "test.txt")
        with open(f, "w") as fp:
            fp.write("hello")
        h1 = compute_local_file_hash(f)
        self.assertEqual(len(h1), 32)  # MD5 hex

        with open(f, "w") as fp:
            fp.write("world")
        h2 = compute_local_file_hash(f)
        self.assertNotEqual(h1, h2)

    def test_compute_hash_missing_file(self):
        from builtin_ops import compute_local_file_hash
        result = compute_local_file_hash("/nonexistent/file.txt")
        self.assertEqual(result, "")


class TestAdapterParser(unittest.TestCase):
    """测试 adapter.yaml 解析器"""

    def _make_adapter(self, **overrides):
        base = {
            "provider": "test",
            "version": "1.0",
            "auth_type": "api-key",
            "deploy_steps": [
                {"id": "step1", "type": "script", "script": "echo ok"}
            ],
            "drift_detection": {"method": "file_hash", "files": ["/etc/hosts"]},
        }
        base.update(overrides)
        return base

    def test_validate_valid(self):
        from adapter_parser import validate_adapter
        validate_adapter(self._make_adapter())  # 不应抛出异常

    def test_validate_missing_field(self):
        from adapter_parser import validate_adapter
        data = self._make_adapter()
        del data["provider"]
        with self.assertRaises(ValueError):
            validate_adapter(data)

    def test_validate_invalid_auth_type(self):
        from adapter_parser import validate_adapter
        with self.assertRaises(ValueError):
            validate_adapter(self._make_adapter(auth_type="invalid"))

    def test_validate_duplicate_step_id(self):
        from adapter_parser import validate_adapter
        data = self._make_adapter(deploy_steps=[
            {"id": "step1", "type": "script", "script": "echo 1"},
            {"id": "step1", "type": "script", "script": "echo 2"},
        ])
        with self.assertRaises(ValueError):
            validate_adapter(data)

    def test_validate_invalid_builtin_action(self):
        from adapter_parser import validate_adapter
        data = self._make_adapter(deploy_steps=[
            {"id": "step1", "type": "builtin", "action": "nonexistent"}
        ])
        with self.assertRaises(ValueError):
            validate_adapter(data)

    def test_render_template(self):
        from adapter_parser import render_template
        result = render_template("pools={{ pools }}, index={{ index }}", {"pools": 4, "index": 2})
        self.assertEqual(result, "pools=4, index=2")

    def test_render_template_missing_var(self):
        from adapter_parser import render_template
        with self.assertRaises(ValueError):
            render_template("{{ undefined_var }}", {})

    def test_expand_for_each(self):
        from adapter_parser import expand_for_each_steps
        steps = [
            {"id": "normal", "type": "script", "script": "echo ok"},
            {"id": "auth", "type": "manual", "for_each": "pool", "instruction": "Pool {{ index }}"},
        ]
        expanded = expand_for_each_steps(steps, 3)
        self.assertEqual(len(expanded), 4)  # 1 normal + 3 pool steps
        self.assertEqual(expanded[1]["_pool_index"], 1)
        self.assertEqual(expanded[3]["_pool_index"], 3)


class TestStateManager(unittest.TestCase):
    """测试状态管理系统"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # 临时切换工作目录
        self.orig_dir = os.getcwd()
        os.chdir(self.tmp)
        # 创建必要目录
        Path(".aipool/state").mkdir(parents=True)
        Path(".aipool/backups").mkdir(parents=True)

    def tearDown(self):
        os.chdir(self.orig_dir)

    def test_init_and_save_load_state(self):
        from state_manager import init_state, save_state, load_state
        state = init_state("test-server", "claude-code", "1.0", 4)
        save_state("test-server", state)
        loaded = load_state("test-server")
        self.assertEqual(loaded["provider"], "claude-code")
        self.assertEqual(loaded["pool_count"], 4)

    def test_load_state_missing(self):
        from state_manager import load_state
        result = load_state("nonexistent-server")
        self.assertIsNone(result)

    def test_update_step_status(self):
        from state_manager import init_state, update_step_status, is_step_done
        state = init_state("s", "p", "1.0", 2)
        self.assertFalse(is_step_done(state, "step1"))
        state = update_step_status(state, "step1", "done")
        self.assertTrue(is_step_done(state, "step1"))

    def test_backup_on_save(self):
        from state_manager import init_state, save_state
        state = init_state("test-server", "claude-code", "1.0", 2)
        save_state("test-server", state)
        # 第二次保存应创建备份
        save_state("test-server", state)
        backups = list(Path(".aipool/backups").glob("test-server-*.json"))
        self.assertGreater(len(backups), 0)

    def test_load_inventory_empty(self):
        from state_manager import load_inventory
        Path(".aipool").mkdir(exist_ok=True)
        with open(".aipool/inventory.yaml", "w") as f:
            f.write("servers: {}\n")
        data = load_inventory()
        self.assertEqual(data["servers"], {})

    def test_load_inventory_missing(self):
        from state_manager import load_inventory
        # 删除 inventory.yaml
        inv = Path(".aipool/inventory.yaml")
        if inv.exists():
            inv.unlink()
        with self.assertRaises(FileNotFoundError):
            load_inventory()


if __name__ == "__main__":
    unittest.main(verbosity=2)
