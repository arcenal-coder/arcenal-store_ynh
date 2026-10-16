from __future__ import annotations

import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
OFFICIAL = {"id": "default", "url": "https://app.yunohost.org/default"}
CUSTOM = {"id": "custom", "url": "https://example.org/catalog", "extra": True}
ARCENAL_URL = "https://raw.githubusercontent.com/arcenal-coder/arcenal-systeme-catalogue/main/"


class StoreTest(unittest.TestCase):
    def run_catalogue(self, directory, action="arcenal_ecrire_catalogue", channel="stable"):
        return subprocess.run(
            [
                "bash", "-e", "-c",
                '''source "$1"
arcenal_fichier_catalogue() { printf '%s/catalogue.yml' "$directory"; }
arcenal_sauvegarde_catalogue() { printf '%s/previous.yml' "$directory"; }
directory="$2"
ynh_app_setting_get() { printf '%s' "$channel"; }
ynh_app_setting_set() { :; }
channel="$4"
"$3"
''',
                "bash", str(ROOT / "scripts" / "_common.sh"), str(directory), action, channel,
            ],
            capture_output=True, text=True,
        )

    def test_catalogues_coexist_and_channel_changes_are_idempotent(self):
        for initial in (
            None, [], [OFFICIAL, CUSTOM], [{"id": "arcenal", "url": "old"}],
            [OFFICIAL, CUSTOM, {"id": "arcenal", "url": "old"}, {"id": "arcenal", "url": "duplicate"}],
            [{"id": "default", "url": None}],
        ):
            with self.subTest(initial=initial), tempfile.TemporaryDirectory() as directory:
                catalogue = Path(directory) / "catalogue.yml"
                if initial is not None:
                    catalogue.write_text(yaml.safe_dump(initial))
                for channel in ("stable", "stable", "preview"):
                    result = self.run_catalogue(directory, channel=channel)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    sources = yaml.safe_load(catalogue.read_text())
                    expected = [OFFICIAL]
                    if initial and CUSTOM in initial:
                        expected.append(CUSTOM)
                    expected.append({"id": "arcenal", "url": ARCENAL_URL + channel})
                    self.assertEqual(sources, expected)
                self.assertEqual(catalogue.stat().st_mode & 0o777, 0o644)

    def test_legacy_upgrade_recovers_sources_without_resurrecting_later_removals(self):
        with tempfile.TemporaryDirectory() as directory:
            catalogue = Path(directory) / "catalogue.yml"
            catalogue.write_text(yaml.safe_dump([{"id": "arcenal", "url": "old"}]))
            backup = Path(directory) / "previous.yml"
            backup.write_text(yaml.safe_dump([OFFICIAL, CUSTOM]))
            original_backup = backup.read_bytes()
            result = self.run_catalogue(directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(CUSTOM, yaml.safe_load(catalogue.read_text()))
            catalogue.write_text(yaml.safe_dump([OFFICIAL]))
            result = self.run_catalogue(directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(CUSTOM, yaml.safe_load(catalogue.read_text()))
            self.assertEqual(backup.read_bytes(), original_backup)

    def test_removal_preserves_current_sources_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            catalogue = Path(directory) / "catalogue.yml"
            catalogue.write_text(yaml.safe_dump([
                OFFICIAL, CUSTOM, {"id": "arcenal", "url": "old"},
            ]))
            (Path(directory) / "previous.yml").write_text(yaml.safe_dump([OFFICIAL]))
            for _ in range(2):
                result = self.run_catalogue(directory, action="arcenal_restaurer_catalogue")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(yaml.safe_load(catalogue.read_text()), [OFFICIAL, CUSTOM])

    def test_invalid_catalogue_is_never_overwritten(self):
        for content in ("[broken", "unexpected: mapping", "- id: missing-url"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                catalogue = Path(directory) / "catalogue.yml"
                catalogue.write_text(content)
                result = self.run_catalogue(directory)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(catalogue.read_text(), content)

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
        self.assertIn("arcenal_ecrire_catalogue", restore)
        self.assertLess(restore.index("ynh_restore_everything"), restore.index("arcenal_ecrire_catalogue"))

    def test_lifecycle_scripts_load_their_common_file_from_any_directory(self) -> None:
        scripts = ("install", "upgrade", "remove", "backup", "restore", "config")
        for script_name in scripts:
            script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")
            self.assertIn('source "$(dirname "$0")/_common.sh"', script)

    def test_panel_exposes_status_and_immediate_catalog_action(self) -> None:
        panel = tomllib.loads((ROOT / "config_panel.toml").read_text(encoding="utf-8"))
        channel = panel["catalogue"]["canal"]["catalogue_channel"]
        self.assertEqual(channel["type"], "select")
        self.assertEqual(channel["choices"], ["stable", "preview"])
        self.assertEqual(channel["default"], "stable")
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
        self.assertIn('app="arcenal-store"', synchronizer)
        self.assertNotIn('readonly app="arcenal-store"', synchronizer)
        self.assertIn("run__actualiser_catalogue", config)
        self.assertIn("arcenal_synchroniser_catalogue", config)
        self.assertNotIn("systemctl start --wait", config)

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

    def test_channel_validation_accepts_only_published_channels(self) -> None:
        script = ROOT / "scripts" / "_common.sh"
        for channel in ("stable", "preview"):
            result = subprocess.run(
                ["bash", "-c", 'source "$1"; arcenal_normaliser_canal "$2"', "bash", str(script), channel],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.stdout, channel)
        rejected = subprocess.run(
            ["bash", "-c", 'source "$1"; arcenal_normaliser_canal "$2"', "bash", str(script), "invalid"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(rejected.stdout, "")

    def test_upgrade_preserves_or_initializes_the_catalog_channel(self) -> None:
        common = (ROOT / "scripts" / "_common.sh").read_text(encoding="utf-8")
        install = (ROOT / "scripts" / "install").read_text(encoding="utf-8")
        upgrade = (ROOT / "scripts" / "upgrade").read_text(encoding="utf-8")
        self.assertIn("arcenal_initialiser_canal", common)
        self.assertIn("arcenal_initialiser_canal", install)
        self.assertIn("arcenal_initialiser_canal", upgrade)

    def test_catalogue_url_tracks_the_selected_channel(self) -> None:
        common = (ROOT / "scripts" / "_common.sh").read_text(encoding="utf-8")
        self.assertIn('ynh_app_setting_set --key=catalogue_url --value="$url"', common)


if __name__ == "__main__":
    unittest.main()
