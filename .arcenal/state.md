# État du projet

Statut : ACTUEL

## Lot actif

- Coexistence des catalogues officiel YunoHost et ARCenal : correction `1.2.0~ynh4` publiée dans les catalogues development, preview et stable.

## Dernière étape validée

- Publication du paquet `3a510983b4c832e442ca259901ae89882867c9dc`, fusion de la PR catalogue #21 après contrôles, promotions sélectives et vérification HTTP des flux publics.
- Recette sur serveur YunoHost encore à effectuer ; publication autorisée par le client en connaissance de cette limite.

## Fichiers importants modifiés

- `scripts/_common.sh` : fusion des sources, récupération de la configuration historique, écriture atomique et retrait ciblé d'ARCenal.
- `scripts/restore`, `scripts/remove` : adaptation du cycle de vie.
- `manifest.toml` : version `1.2.0~ynh4`.
- `tests/test_store.py`, `README.md` : régressions exécutables et documentation.
- `.arcenal/` : initialisation par le helper officiel et contexte projet.

## Tests exécutés

- PASS : 15 tests via `python3 -m unittest discover -s tests -v`, dont fonctions Bash exécutées sur fichiers temporaires.
- PASS : `bash -n` sur les huit scripts de cycle de vie et synchronisation.
- PASS : `git diff --check`.
- PASS : 18 tests du catalogue, cohérence des trois flux v3/manifestes v1 et contrôle GitHub de la PR #21.
- PASS : promotions development → preview puis preview → stable, uniquement `application=arcenal-store`.
- PASS : HTTP des six flux bruts publics v1/v3 ; version `1.2.0~ynh4` et révision `3a510983b4c832e442ca259901ae89882867c9dc` vérifiées dans les trois canaux ; miroir Pages stable vérifié également.
- Environnement local : PyYAML absent du Python système ; tests exécutés dans un environnement virtuel temporaire avec PyYAML 6.0.3.
- NON TESTÉ : installation, upgrade, sauvegarde/restauration et synchronisation réelle sur serveur YunoHost.

## Résultats

- Cause corrigée : l'ancienne fonction `arcenal_ecrire_catalogue` remplaçait toute la liste par ARCenal seul.
- Les sources tierces sont conservées et le catalogue officiel est réactivé ; le canal stable/preview reste respecté sans doublon ARCenal.
- En cas de YAML invalide, la configuration existante reste intacte.
- Cause de l'absence de mise à jour : les catalogues pointaient encore vers `1.2.0~ynh3`, malgré le push du paquet. Référence désormais corrigée.
- Catalogue : https://github.com/arcenal-coder/arcenal-systeme-catalogue/pull/21 ; preuves de publication dans le commentaire final et `acceptance/STORE_CATALOGUE_TEST_REPORT.md`.
- Les autres références de diffusion ARCenal sont inchangées. Le générateur existant a rafraîchi les métadonnées officielles stable : Nextcloud `35.0.2~ynh1`, niveau Vaultwarden 6.

## Blocages

- Aucun connu.

## Décisions récentes

- Voir `decisions.md` pour la coexistence, la migration historique et le retrait ciblé.

## Prochaine action

- Actualiser les catalogues dans la WebAdmin puis réaliser la recette sur YunoHost : upgrade du Store, présence des deux catalogues et mises à jour usuelles disponibles. Aucun accès serveur utilisé ; déploiement à autoriser séparément.
