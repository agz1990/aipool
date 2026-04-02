#!/usr/bin/env python3
"""
adapter.yaml 验证测试
测试 claude-code-pool/adapter.yaml 是否符合规范
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))


class TestClaudeCodeAdapter(unittest.TestCase):
    """测试 claude-code-pool adapter.yaml"""

    def setUp(self):
        from adapter_parser import load_adapter
        adapter_path = Path(__file__).parent.parent.parent / "aipool/claude-code-pool"
        self.adapter = load_adapter(adapter_path)

    def test_required_fields(self):
        self.assertEqual(self.adapter["provider"], "claude-code")
        self.assertIn("version", self.adapter)
        self.assertEqual(self.adapter["auth_type"], "interactive")

    def test_has_pre_checks(self):
        checks = self.adapter.get("pre_checks", [])
        self.assertGreater(len(checks), 0)
        ids = [c["id"] for c in checks]
        self.assertIn("check_os", ids)
        self.assertIn("check_disk", ids)

    def test_has_deploy_steps(self):
        steps = self.adapter.get("deploy_steps", [])
        self.assertGreater(len(steps), 0)
        ids = [s["id"] for s in steps]
        self.assertIn("create_shared_dirs", ids)
        self.assertIn("run_setup", ids)
        self.assertIn("auth_login", ids)

    def test_auth_login_is_manual_for_each(self):
        steps = {s["id"]: s for s in self.adapter.get("deploy_steps", [])}
        auth = steps.get("auth_login", {})
        self.assertEqual(auth.get("type"), "manual")
        self.assertEqual(auth.get("for_each"), "pool")
        self.assertIn("instruction", auth)

    def test_drift_detection_has_files(self):
        dd = self.adapter.get("drift_detection", {})
        self.assertEqual(dd.get("method"), "file_hash")
        files = dd.get("files", [])
        self.assertGreater(len(files), 0)

    def test_has_health_checks(self):
        checks = self.adapter.get("health_checks", [])
        self.assertGreater(len(checks), 0)

    def test_has_rollback(self):
        rollback = self.adapter.get("rollback", {})
        self.assertIn("backup_path", rollback)
        self.assertIn("steps", rollback)

    def test_step_ids_unique(self):
        steps = self.adapter.get("deploy_steps", [])
        ids = [s["id"] for s in steps]
        self.assertEqual(len(ids), len(set(ids)))

    def test_template_vars_in_auth_login(self):
        steps = {s["id"]: s for s in self.adapter.get("deploy_steps", [])}
        auth = steps.get("auth_login", {})
        instruction = auth.get("instruction", "")
        self.assertIn("{{ index }}", instruction)


if __name__ == "__main__":
    unittest.main(verbosity=2)
