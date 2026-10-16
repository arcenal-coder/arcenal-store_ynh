# État du projet

Statut : ACTUEL

## Lot actif

- Coexistence des catalogues officiel YunoHost et ARCenal : correction `1.2.0~ynh4` développée et vérifiée localement ; publication GitHub autorisée.

## Dernière étape validée

- Correction et vérifications locales ; recette sur serveur YunoHost encore à effectuer.

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
- Environnement local : PyYAML absent du Python système ; tests exécutés dans un environnement virtuel temporaire avec PyYAML 6.0.3.
- NON TESTÉ : installation, upgrade, sauvegarde/restauration et synchronisation réelle sur serveur YunoHost.

## Résultats

- Cause corrigée : l'ancienne fonction `arcenal_ecrire_catalogue` remplaçait toute la liste par ARCenal seul.
- Les sources tierces sont conservées et le catalogue officiel est réactivé ; le canal stable/preview reste respecté sans doublon ARCenal.
- En cas de YAML invalide, la configuration existante reste intacte.

## Blocages

- Aucun connu.

## Décisions récentes

- Voir `decisions.md` pour la coexistence, la migration historique et le retrait ciblé.

## Prochaine action

- Après publication GitHub, réaliser la recette sur YunoHost : upgrade du Store, présence des deux catalogues et mises à jour usuelles disponibles. Déploiement à autoriser séparément.
