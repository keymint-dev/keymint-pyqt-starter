"""Tests get_host_id() against a temporary installation-ID file. Offline only:
no API calls are made. Run: python -m unittest discover tests"""
import hashlib
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# license_manager builds a KeyMint client at import, which needs a non-empty key.
os.environ.setdefault("KEYMINT_CLIENT_API_KEY", "km_live_unit_test_placeholder")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import license_manager  # noqa: E402
from license_manager import HostIdError, get_host_id  # noqa: E402


class HostIdTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "keymint" / "installation-id"
        patcher = mock.patch.object(license_manager, "INSTALLATION_ID_PATH", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_stable_full_length_sha256(self):
        first = get_host_id()
        self.assertRegex(first, re.compile(r"^[0-9a-f]{64}$"))
        self.assertTrue(self.path.is_file())
        self.assertEqual(get_host_id(), first)

    def test_reuses_saved_id(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("existing-installation", encoding="utf-8")
        expected = hashlib.sha256(b"existing-installation").hexdigest()
        self.assertEqual(get_host_id(), expected)

    def test_unique_per_installation(self):
        first = get_host_id()
        self.path.unlink()
        self.assertNotEqual(get_host_id(), first)

    def test_unsaved_id_raises_instead_of_falling_back(self):
        # The parent "directory" is a file, so the ID can't be saved.
        blocker = Path(self.tmp.name) / "blocker"
        blocker.write_text("", encoding="utf-8")
        with mock.patch.object(license_manager, "INSTALLATION_ID_PATH", blocker / "installation-id"):
            with self.assertRaises(HostIdError):
                get_host_id()

    def test_activation_reports_host_id_error(self):
        with mock.patch.object(license_manager, "get_host_id", side_effect=HostIdError("no id")), \
                mock.patch.object(license_manager.client, "activate_key") as activate:
            result = license_manager.activate_license("KEY")
        self.assertEqual(result, {"success": False, "message": "no id"})
        activate.assert_not_called()

    def test_offline_check_reports_host_id_error(self):
        with mock.patch.object(license_manager, "get_host_id", side_effect=HostIdError("no id")):
            result = license_manager._check_offline("contents")
        self.assertEqual(result, {"success": False, "message": "no id"})


if __name__ == "__main__":
    unittest.main()
