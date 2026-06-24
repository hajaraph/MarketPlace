# Marketplace Maps Mobile

Application mobile pour la place de marché globale.

## État du projet

- **Navigation :** La page **Explore** est la page d'accueil par défaut (`/`).
- **Authentification :** Système de redirection en place, mais la page d'accueil est accessible publiquement pour permettre la découverte des produits.
- **Thème :** Material 3 avec des jetons de design personnalisés (AppColors, AppTypography).

## Modifications récentes

- Correction du routeur pour afficher la page Explore en premier.
- Harmonisation des routes (`AppRoutes.home` -> `/`).

## Prochaines étapes

- Implémenter la page de connexion réelle (actuellement un Placeholder).
- Protéger les onglets "Orders" et "Profile" pour qu'ils redirigent vers la connexion si non authentifié.
