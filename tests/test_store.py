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
        scripts = ("install", "upgrade", "remove", "backup", "restore", "config")
        for script_name in scripts:
            script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")
            self.assertIn('source "$(dirname "$0")/_common.sh"', script)

    def test_panel_exposes_status_and_immediate_catalog_action(self) -> None:
        panel = tomllib.loads((ROOT / "config_panel.toml").read_text(encoding="utf-8"))
        options = panel["catalogue"]["etat"]
        self.assertTrue(options["catalogue_last_sync_at"]["readonly"])
        self.assertTrue(options["catalogue_last_sync_result"]["readonly"])
        action = panel["catalogue"]["actions"]["actualiser_catalogue"]
        self.assertEqual(action["type"], "button")
        self.assertEqual(action["style"], "success")

    def test_synchronizer_records_success_and_fails_closed(self) -> None:
        common = (ROOT / "scripts" / "_common.sh").read_text(encoding="utf-8")
        synchronizer = (ROOT / "scripts" / "synchroniser-catalogue").read_text(encoding="utf-8")
        config = (ROOT / "scripts" / "config").read_text(encoding="utf-8")
        self.assertIn("catalogue_last_sync_at", common)
        self.assertIn("catalogue_last_sync_result", common)
        self.assertIn('"success" "Catalogue ARCenal synchronisé."', common)
        self.assertIn("arcenal_echouer_synchronisation", common)
        self.assertIn("arcenal_verrouiller_synchronisation", common)
        self.assertIn("flock 9", common)
        self.assertIn("arcenal_synchroniser_catalogue", synchronizer)
        self.assertNotIn("flock", synchronizer)
        self.assertIn("run__actualiser_catalogue", config)
        self.assertIn('systemctl start --wait "${app}-catalogue.service"', config)

    def test_scheduler_is_deployed_and_removed_with_the_store(self) -> None:
        common = (ROOT / "scripts" / "_common.sh").read_text(encoding="utf-8")
        install = (ROOT / "scripts" / "install").read_text(encoding="utf-8")
        remove = (ROOT / "scripts" / "remove").read_text(encoding="utf-8")
        timer = (ROOT / "conf" / "arcenal-store-catalogue.timer").read_text(encoding="utf-8")
        self.assertIn("arcenal_deployer_synchronisation", install)
        self.assertIn("arcenal_retirer_synchronisation", remove)
        self.assertLess(install.index("arcenal_synchroniser_catalogue"), install.index("arcenal_deployer_synchronisation"))
        self.assertIn('systemctl enable --now "${app}-catalogue.timer"', common)
        self.assertIn('systemctl stop "${app}-catalogue.service"', common)
        self.assertIn("OnCalendar=*-*-* 03:05:00", timer)


if __name__ == "__main__":
    unittest.main()
