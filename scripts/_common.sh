#!/bin/bash

arcenal_url_catalogue() {
    printf '%s' 'https://raw.githubusercontent.com/arcenal-coder/arcenal-systeme-catalogue/main/stable'
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

arcenal_ecrire_catalogue() {
    local catalogue url
    catalogue="$(arcenal_fichier_catalogue)"
    url="$(arcenal_url_catalogue)"
    printf '%s\n' '- id: arcenal' "  url: ${url}" > "$catalogue"
    chmod 0644 "$catalogue"
}

arcenal_restaurer_catalogue() {
    local catalogue sauvegarde
    catalogue="$(arcenal_fichier_catalogue)"
    sauvegarde="$(arcenal_sauvegarde_catalogue)"
    if test -f "$sauvegarde"; then
        cp --preserve=mode,timestamps "$sauvegarde" "$catalogue"
        return 0
    fi
    test -f "${sauvegarde}.absent" && ynh_safe_rm "$catalogue"
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
