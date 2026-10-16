#!/bin/bash

arcenal_normaliser_canal() {
    local canal="${1:-stable}"
    case "$canal" in
        stable|preview) printf '%s' "$canal" ;;
        *) return 1 ;;
    esac
}

arcenal_canal_catalogue() {
    local canal
    canal="$(ynh_app_setting_get --key=catalogue_channel)"
    arcenal_normaliser_canal "${canal:-stable}"
}

arcenal_initialiser_canal() {
    local canal
    canal="$(ynh_app_setting_get --key=catalogue_channel)"
    test -n "$canal" || ynh_app_setting_set --key=catalogue_channel --value=stable
}

arcenal_url_catalogue() {
    local canal
    canal="$(arcenal_canal_catalogue)" || return 1
    printf '%s/%s' 'https://raw.githubusercontent.com/arcenal-coder/arcenal-systeme-catalogue/main' "$canal"
}

arcenal_fichier_catalogue() {
    printf '%s' '/etc/yunohost/apps_catalog.yml'
}

arcenal_sauvegarde_catalogue() {
    printf '/etc/yunohost/apps/%s/catalogue-pre-arcenal.yml' "$app"
}

arcenal_verifier_catalogue() {
    local url
    url="$(arcenal_url_catalogue)"
    curl --fail --silent --show-error "${url}/v3/apps.json" > /dev/null
}

arcenal_sauvegarder_catalogue() {
    local catalogue sauvegarde
    catalogue="$(arcenal_fichier_catalogue)"
    sauvegarde="$(arcenal_sauvegarde_catalogue)"
    test -f "$sauvegarde" && return 0
    if test -f "$catalogue"; then
        cp --preserve=mode,timestamps "$catalogue" "$sauvegarde"
        return 0
    fi
    : > "${sauvegarde}.absent"
}

arcenal_modifier_catalogues() {
    local catalogue sauvegarde url
    catalogue="$(arcenal_fichier_catalogue)"
    sauvegarde="$(arcenal_sauvegarde_catalogue)"
    url="$2"
    python3 - "$catalogue" "$sauvegarde" "$1" "$url" <<'PY'
import os
import sys
import tempfile
from pathlib import Path

import yaml

catalogue, sauvegarde = map(Path, sys.argv[1:3])
action, url = sys.argv[3:5]


def lire(path):
    if not path.exists():
        return []
    sources = yaml.safe_load(path.read_text())
    if sources is None:
        return []
    if not isinstance(sources, list) or any(
        not isinstance(source, dict)
        or not isinstance(source.get("id"), str)
        or "url" not in source
        or (source["url"] is not None and not isinstance(source["url"], str))
        for source in sources
    ):
        raise ValueError(f"Configuration des catalogues invalide : {path}")
    return sources


sources = [source for source in lire(catalogue) if source["id"] != "arcenal"]
if action == "ajouter" and not sources:
    # Recover sources hidden by versions that replaced the whole configuration.
    ids = {source["id"] for source in sources}
    for source in lire(sauvegarde):
        if source["id"] != "arcenal" and source["id"] not in ids:
            sources.append(source)
            ids.add(source["id"])

officiel = next((source for source in sources if source["id"] == "default"), None)
if officiel is None:
    sources.insert(0, {"id": "default", "url": "https://app.yunohost.org/default"})
else:
    officiel["url"] = "https://app.yunohost.org/default"
if action == "ajouter":
    sources.append({"id": "arcenal", "url": url})

# Write atomically so a failed conversion never leaves a truncated configuration.
fd, temporary = tempfile.mkstemp(prefix=".apps_catalog-", dir=catalogue.parent)
try:
    with os.fdopen(fd, "w") as stream:
        yaml.safe_dump(sources, stream, sort_keys=False)
        stream.flush()
        os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), 0o644)
    os.replace(temporary, catalogue)
finally:
    if os.path.exists(temporary):
        os.unlink(temporary)
PY
}

arcenal_ecrire_catalogue() {
    local url
    url="$(arcenal_url_catalogue)" || return 1
    arcenal_modifier_catalogues ajouter "$url" || return 1
    ynh_app_setting_set --key=catalogue_url --value="$url"
}

arcenal_restaurer_catalogue() {
    arcenal_modifier_catalogues retirer ""
}

arcenal_actualiser_catalogue() {
    yunohost tools update apps
}

arcenal_repertoire_synchronisation() {
    printf '/usr/local/lib/%s' "$app"
}

arcenal_verrouiller_synchronisation() {
    exec 9>"/run/${app}-catalogue.lock"
    flock 9
}

arcenal_enregistrer_synchronisation() {
    local date="$1" resultat="$2" message="$3"
    ynh_app_setting_set --key=catalogue_last_sync_at --value="$date"
    ynh_app_setting_set --key=catalogue_last_sync_result --value="$resultat"
    ynh_app_setting_set --key=catalogue_last_sync_message --value="$message"
}

arcenal_echouer_synchronisation() {
    local message="$1"
    arcenal_enregistrer_synchronisation "$(date --iso-8601=seconds)" "error" "$message"
    ynh_die "$message"
}

arcenal_synchroniser_catalogue() {
    arcenal_verrouiller_synchronisation
    arcenal_verifier_catalogue || arcenal_echouer_synchronisation "Le catalogue ARCenal est momentanément indisponible."
    arcenal_ecrire_catalogue || arcenal_echouer_synchronisation "La source du catalogue ARCenal n'a pas pu être configurée."
    arcenal_actualiser_catalogue || arcenal_echouer_synchronisation "YunoHost n'a pas pu actualiser le catalogue ARCenal."
    arcenal_enregistrer_synchronisation "$(date --iso-8601=seconds)" "success" "Catalogue ARCenal synchronisé."
}

arcenal_configurer_planification() {
    systemctl daemon-reload
    systemctl enable --now "${app}-catalogue.timer"
}

arcenal_deployer_synchronisation() {
    local repertoire
    repertoire="$(arcenal_repertoire_synchronisation)"
    install -d -m 0755 "$repertoire"
    install -m 0755 "${YNH_APP_BASEDIR}/scripts/synchroniser-catalogue" "${repertoire}/synchroniser-catalogue"
    install -m 0644 "${YNH_APP_BASEDIR}/conf/${app}-catalogue.service" "/etc/systemd/system/${app}-catalogue.service"
    install -m 0644 "${YNH_APP_BASEDIR}/conf/${app}-catalogue.timer" "/etc/systemd/system/${app}-catalogue.timer"
    arcenal_configurer_planification
}

arcenal_retirer_synchronisation() {
    local repertoire
    repertoire="$(arcenal_repertoire_synchronisation)"
    systemctl disable --now "${app}-catalogue.timer" 2>/dev/null || true
    systemctl stop "${app}-catalogue.service" 2>/dev/null || true
    rm -f "/etc/systemd/system/${app}-catalogue.service" "/etc/systemd/system/${app}-catalogue.timer" "${repertoire}/synchroniser-catalogue"
    rmdir "$repertoire" 2>/dev/null || true
    systemctl daemon-reload
}

arcenal_systeme_est_installe() {
    test -d /etc/yunohost/apps/arcenal-systeme
}
