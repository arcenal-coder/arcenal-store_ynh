# ARCenal Store pour YunoHost

ARCenal Store est le point de départ d'une installation ARCenal. Il ajoute le
catalogue ARCenal contrôlé à YunoHost sans modifier le cœur ni la WebAdmin.

Le catalogue officiel YunoHost reste actif à côté du catalogue ARCenal : les
applications usuelles et leurs mises à jour restent disponibles dans la même
interface YunoHost. Les autres catalogues configurés sont conservés.

La version `1.2.0~ynh4` rétablit cette coexistence lors de la mise à jour du
Store, y compris si une ancienne version avait masqué le catalogue officiel.
Si ARCenal est la seule source restante, les sources présentes dans la sauvegarde
créée avant son installation sont également récupérées. La désinstallation
retire uniquement la source ARCenal, sans remplacer les autres sources par une
ancienne configuration.

## Parcours client

1. Dans **Applications → Installer une application**, utilisez l'installation
   par URL avec `https://github.com/arcenal-coder/arcenal-store_ynh`.
2. Revenez dans **Applications → Installer une application**, recherchez
   **ARCenal Système**, puis installez-le comme toute autre application.

La première étape est temporairement une installation par URL car YunoHost ne
peut pas afficher un catalogue qui n'est pas encore installé. Après sa
publication dans le catalogue communautaire officiel YunoHost, ARCenal Store
pourra être sélectionné directement dans le store standard.

La désinstallation d'ARCenal Store est volontairement bloquée tant qu'ARCenal
Système est présent, afin de ne jamais rompre les mises à jour de ce dernier.

## Synchronisation du catalogue

ARCenal Store actualise le catalogue chaque jour. Dans la page de configuration
de l'application, la section **Catalogue ARCenal** affiche la dernière
synchronisation et son résultat ; le bouton **Actualiser le catalogue** lance
la même opération immédiatement. Aucun accès SSH n'est nécessaire.

Le canal **Stable** reste sélectionné par défaut. Pour réaliser la recette
d’une candidate, choisissez **Prévisualisation**, sauvegardez, puis utilisez
**Actualiser le catalogue**. Les applications déjà installées sont alors
proposées comme des mises à jour YunoHost normales ; aucun fichier applicatif
n’est copié manuellement sur le serveur.

## Vérifications locales

Les tests nécessitent Python >= 3.11 et PyYAML (déjà fourni par YunoHost sur le
serveur). Sur un poste de développement, installer PyYAML dans un environnement
virtuel, puis lancer `python3 -m unittest discover -s tests -v`.
