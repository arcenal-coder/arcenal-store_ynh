from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class StoreTest(unittest.TestCase):
    def test_manifest_is_a_non_web_catalog_installer(self) -> None:
        manifest = tomllib.loads((ROOT / "manifest.toml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "arcenal-store")
        self.assertFalse(manifest["integration"]["sso"])
        self.assertEqual(manifest["install"], {})
        self.assertEqual(manifest["resources"], {})

    def test_store_owns_only_the_catalog_configuration(self) -> None:
        common = (ROOT / "scripts" / "_common.sh").read_text(encoding="utf-8")
        self.assertIn("apps_catalog.yml", common)
        self.assertNotIn("/usr/share/yunohost/portal", common)
        self.assertNotIn("/etc/ssowat", common)

    def test_removal_protects_an_installed_system(self) -> None:
        remove = (ROOT / "scripts" / "remove").read_text(encoding="utf-8")
        common = (ROOT / "scripts" / "_common.sh").read_text(encoding="utf-8")
        self.assertIn("arcenal_systeme_est_installe && ynh_die", remove)
        self.assertIn("test -d /etc/yunohost/apps/arcenal-systeme", common)

    def test_restore_uses_the_helper_with_no_missing_argument(self) -> None:
        restore = (ROOT / "scripts" / "restore").read_text(encoding="utf-8")
        self.assertIn("ynh_restore_everything", restore)

    def test_lifecycle_scripts_load_their_common_file_from_any_directory(self) -> None:
        scripts = ("install", "upgrade", "remove", "backup", "restore")
        for script_name in scripts:
            script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")
            self.assertIn('source "$(dirname "$0")/_common.sh"', script)


if __name__ == "__main__":
    unittest.main()
