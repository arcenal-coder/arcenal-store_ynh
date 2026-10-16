# Architecture

Statut : ACTUEL

- Paquet YunoHost v2, helpers 2.1 ; scripts Bash de cycle de vie.
- `scripts/_common.sh` centralise les sources, les canaux et la synchronisation planifiée par systemd.
- Modification ciblée de `/etc/yunohost/apps_catalog.yml` par Python 3 et PyYAML (dépendance YunoHost), validation avant écriture et remplacement atomique.
- La restauration normalise les sources après `ynh_restore_everything` ; la sauvegarde existante conserve la configuration et les réglages du paquet.
- Tests locaux Python/unittest avec exécution réelle des fonctions Bash sur des fichiers temporaires ; installation réelle à vérifier sur YunoHost.
