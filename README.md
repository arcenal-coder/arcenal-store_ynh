# ARCenal Store pour YunoHost

ARCenal Store est le point de départ d'une installation ARCenal. Il ajoute le
catalogue ARCenal contrôlé à YunoHost sans modifier le cœur ni la WebAdmin.

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
