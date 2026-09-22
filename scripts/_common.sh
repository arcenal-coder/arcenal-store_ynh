#!/bin/bash

arcenal_url_catalogue() {
    printf '%s' 'https://arcenal-coder.github.io/arcenal-systeme-catalogue/stable'
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
    curl --fail --silent --show-error "${url}/v3/apps.json" > /dev/null || ynh_die "Le catalogue ARCenal est momentanément indisponible."
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

arcenal_systeme_est_installe() {
    test -d /etc/yunohost/apps/arcenal-systeme
}
