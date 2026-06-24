# Marketplace Maps

Plateforme de commerce électronique décentralisée géolocalisée, connectant acheteurs et vendeurs à travers une marketplace cartographique.

## 📋 Vue d'ensemble

**Marketplace Maps** est une application mobile + backend API permettant :
- Aux **vendeurs** de créer des magasins physiques/virtuels et publier des produits
- Aux **clients** de découvrir produits et magasins par localisation géographique
- Aux **administrateurs** de modérer contenu et gérer la plateforme

Stack :
- **Backend** : Django 4+ + Ninja (REST API)
- **Mobile** : Flutter (iOS/Android)
- **Base de données** : PostgreSQL (développement) / SQLite (local)
- **Auth** : JWT avec tokens d'accès/refresh (15min/7j)

## 📁 Structure du projet

```
marketplace_maps/
├── MarketplaceAPI/           # Backend Django
│   ├── api/                  # Routers Ninja (endpoints REST)
│   ├── auth/                 # Authentification JWT
│   ├── users/                # Modèle Utilisateur, roles
│   ├── places/               # Magasins, Centres commerciaux, Emplacements
│   ├── catalog/              # Produits, Médias produits
│   ├── cart/                 # Panier (prix live)
│   ├── orders/               # Commandes (prix/adresse snapshots)
│   ├── shared/               # Utilitaires (models, schemas, API response)
│   ├── manage.py             # Django CLI
│   └── requirements.txt      # Dépendances Python
├── marketplace_maps_mobile/  # App Flutter (iOS/Android)
├── conception.html           # Document de conception (DDD, modèles, endpoints)
└── README.md                 # Ce fichier
```

## 🏗️ Architecture

### Approche DDD Pragmatique

- **Fat Models** : logique métier dans les modèles (Panier.calculer_total(), Commande.annuler())
- **Managers** : repositories pour accès aux données (.vivants(), .supprimes())
- **Services** : orchestration métier (cart/services.py, orders/services.py)
- **Routers** : endpoints HTTP mappant requêtes → services

### Modèles clés

**Utilisateurs & Auth**
- `Utilisateur` : email, téléphone, role (CLIENT/VENDEUR/ADMIN)
- Auth JWT : access_token (15min) + refresh_token (7j) avec rotation + blacklist

**Places**
- `EmplacementMarche` (abstract) → `Magasin` + `CentreCommercial`
- Proprietaire/Vendeur assignment, soft delete

**Catalog**
- `Produit` : FK Magasin, prix_mga (live), quantite (stock)
- `MediaProduit` : images/vidéos associées

**Panier (Live)**
- `Panier` : 1↔1 par Utilisateur
- `LignePanier` : Produit + quantite, sous_total = quantite × prix_live
- Services : ajouter, modifier, retirer, vider + validation stock

**Commandes (Snapshots)**
- `Commande` : snapshot adresse, statut (EN_ATTENTE → CONFIRMÉE → PRÉPARATION → LIVRAISON → LIVRÉE / ANNULÉE)
- `LigneCommande` : snapshot prix + nom produit au moment création
- `AdresseLivraison` : réutilisable par utilisateur
- `HistoriqueVente` : append-only reporting (non supprimable)

## 🚀 Installation & démarrage

### Prérequis
- Python 3.10+
- pip
- PostgreSQL ou SQLite (local)

### Backend

```bash
cd MarketplaceAPI

# Créer venv et installer dépendances
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Tests
python manage.py test

# Lancer serveur (http://localhost:8000)
python manage.py runserver
```

**Endpoint racine** : `http://localhost:8000/api`
Voir [MarketplaceAPI/README.md](MarketplaceAPI/README.md) pour documentation complète des endpoints.

### Mobile

```bash
cd marketplace_maps_mobile

# Installation Flutter (si pas déjà fait)
flutter pub get

# Lancer sur émulateur/device
flutter run
```

## 📡 API

L'API REST utilise **Ninja** (lightweight Django REST). Tous les endpoints retournent une enveloppe standardisée :

```json
{
  "success": true,
  "timestamp": "2026-06-24T10:30:45Z",
  "data": { ... },
  "meta": { ... },
  "message": "OK",
  "error": null
}
```

**Modules API** :
- `/auth` : register, login, refresh, me
- `/places` : magasins, centres commerciaux, validation
- `/catalog` : produits, médias
- `/panier` : articles de panier
- `/commandes` : commandes, adresses, suivi

Voir [MarketplaceAPI/README.md](MarketplaceAPI/README.md) pour exemples détaillés de chaque endpoint (requête/réponse/erreurs).

## 🧪 Tests

**Backend** (64 tests couvrant tous modules) :
```bash
cd MarketplaceAPI
python manage.py test
```

Couverture par module :
- Auth : 8 tests (login, register, JWT, refresh)
- Places : 12 tests (CRUD, validation, permissions)
- Catalog : 12 tests (CRUD médias, structure)
- Cart : 9 tests (ajout, modification, suppression, stock)
- Orders : 12 tests (adresses, création, snapshots, historique)
- Health : misc checks

**Mobile** : à venir

## 📚 Documentation

- **Conception détaillée** : [conception.html](conception.html) — diagrammes ER, endpoints, règles métier
- **API endpoints** : [MarketplaceAPI/README.md](MarketplaceAPI/README.md) — requêtes/réponses/exemples
- **Code** : commentaires sur logique métier complexe uniquement (DRY, SOLID)

## 🔐 Sécurité

- JWT stateless : pas de session server-side
- Tokens rotationnels : refresh génère nouveau access + nouveau refresh
- Blacklist des tokens révoqués
- Permissions : Proprietaire/Vendeur pour création, proprietaire+admin pour modification
- Validation input : Pydantic schemas côté HTTP
- Soft delete : `est_supprime` + `date_suppression` pour audit trail

## 🛠️ Développement

### Conventions

- **Nommage** : snake_case Python, camelCase JSON
- **Modèles** : hériter `TimeStampedModel` (date_création, date_mise_à_jour) ou `SoftDeleteModel` (+ est_supprime)
- **Services** : logique métier en couche service, pas dans views/routers
- **Tests** : TestCase Django, au minimum cas happy path + edge cases
- **Commits** : Messages en FRANÇAIS, descriptifs (feat/fix/refactor/docs/test)

### Ajouter une fonctionnalité

1. **Modèles** : créer app Django (`python manage.py startapp <module>`), définir modèles
2. **Services** : logique métier dans `<module>/services.py`
3. **Schemas** : validation input/output Pydantic
4. **Router** : endpoints dans `api/routers/<module>.py`
5. **Tests** : couvrir cas happy path + erreurs
6. **Docs** : ajouter exemples dans [MarketplaceAPI/README.md](MarketplaceAPI/README.md)

## 📋 Roadmap

Modules implémentés ✅ :
- Auth (JWT, login, register)
- Places (Magasins, Centres commerciaux)
- Catalog (Produits, Médias)
- Cart (Panier live)
- Orders (Commandes avec snapshots)

À implémenter 📋 :
- Payments (Paiement, statuts paiement)
- Delivery (Livraison, suivi avec GPS)
- Reviews (AvisMagasin, AvisProduit)
- Favorites (Produits/Magasins favoris)
- Promotions (Code promotionnel, réductions)
- Notifications (Alertes, messages)
- Moderation (Signalements, approvals)

## 📧 Contact

Responsable projet : dhajarison@gmail.com

---

**Dernière mise à jour** : 2026-06-24
