# Marketplace Maps — Backend API

Backend de la marketplace cartographique, construit avec **Django 6** + **Django Ninja** + **JWT**.

Architecture : **DDD pragmatique sur l'ORM Django** — pas de couche `domain/` séparée ni de mappers. Le model Django EST l'entité (fat model), le manager/QuerySet EST le repository, les use cases vivent dans `services.py`.

---

## 📁 Structure du projet

```
MarketplaceAPI/
├── MarketplaceAPI/          # Package Django (settings, urls, wsgi, asgi)
│   ├── settings.py          # Configuration (DB, JWT, apps, timezone)
│   ├── urls.py              # Montage des routes (admin + API Ninja)
│   ├── wsgi.py
│   └── asgi.py
│
├── api/                     # ★ Couche API (Ninja) — routers minces
│   ├── ninja_api.py         # Instance NinjaAPI — enregistrement des routers
│   └── routers/
│       ├── health.py        # GET /api/health
│       ├── auth.py          # /api/auth/*    (register, login, refresh, me)
│       ├── places.py        # /api/places/*  (magasins, centres commerciaux)
│       ├── catalog.py       # /api/catalog/* (produits, médias)
│       ├── cart.py          # /api/panier*   (panier transitoire)
│       └── orders.py        # /api/*         (commandes, adresses)
│
├── shared/                  # ★ Noyau partagé (mixins + enveloppe API)
│   ├── models.py            # TimeStampedModel, SoftDeleteModel, SoftDeleteQuerySet
│   ├── gps.py               # CoordonneesMixin (latitude/longitude)
│   └── api_response.py      # Envelope + ApiResponse + handlers d'erreur globaux
│
├── users/                   # Utilisateurs + auth (Utilisateur, RoleUtilisateur)
├── places/                  # Magasin, CentreCommercial (EmplacementMarche abstrait)
├── catalog/                 # Produit, MediaProduit (état stock dérivé)
│   # chaque app : models.py + services.py + schemas.py + admin.py + tests.py
│
├── venv/                    # Environnement virtuel Python (non versionné)
├── db.sqlite3               # Base SQLite de dev (non versionnée)
├── requirements.txt          # Dépendances figées
├── manage.py
└── README.md
```

> Les apps métier (`places`, `catalog`, `orders`…) seront ajoutées **module par module** sur le même patron : `models.py` (fat model + manager) → `services.py` (use cases) → `schemas.py` (frontière API) → router Ninja.

---

## ⚡ Stack technique

| Outil | Rôle |
|---|---|
| **Django 6.0.6** | Framework web + ORM |
| **Django Ninja 1.6.2** | API REST (routers + schémas Pydantic) |
| **django-ninja-jwt 5.4.4** | Authentification JWT (access + refresh + rotation) |
| **Pydantic 2.13** | Validation & sérialisation des données |
| **SQLite** | Base de données (dev — PostgreSQL en prod) |
| **Python 3.12** | Runtime |

---

## 🚀 Installation

```bash
# 1. Créer et activer le venv
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Linux/Mac

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Appliquer les migrations
python manage.py migrate

# 4. (Optionnel) Créer un superuser
python manage.py createsuperuser
```

---

## 🏃 Lancement

```bash
python manage.py runserver
```

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/api/docs` | **Swagger UI** — documentation interactive auto-générée ⭐ |
| `http://127.0.0.1:8000/api/openapi.json` | Schéma OpenAPI brut |
| `http://127.0.0.1:8000/admin/` | Interface d'admin Django |
| `http://127.0.0.1:8000/api/health` | Health check `{"status": "ok"}` |

---

## 🏗️ Architecture — DDD pragmatique sur ORM

On garde l'esprit DDD (bounded contexts, séparation des responsabilités) **sans** la lourdeur d'une couche domaine découplée de l'ORM.

```
api/routers/   # Mince : valide l'entrée (schemas), délègue, sérialise la sortie
     │
     ▼
<app>/services.py   # Use cases : orchestration, transactions, règles inter-agrégats
     │
     ▼
<app>/models.py     # Fat model = entité + invariants + comportement
                    # manager / QuerySet = "repository" idiomatique Django
```

**Décisions clés :**

| Concept DDD classique | Choix ici |
|---|---|
| `domain/` à zéro dépendance Django | ❌ Supprimé — l'ORM EST le domaine |
| Mappers Entity ↔ Model | ❌ Supprimés — inutiles |
| Interface `Repository` par agrégat | ❌ Supprimée — `Model.objects` la remplace |
| Requête complexe réutilisée | ✅ Custom `QuerySet`/`Manager` sur le model |
| Logique d'entité | ✅ Méthodes du model (fat model) |
| Orchestration / use case | ✅ `services.py` |
| Bounded context | ✅ Une app Django par contexte |

**Mixins partagés (`shared/`) :**

- `TimeStampedModel` → `date_creation` / `date_mise_a_jour` (audit auto).
- `SoftDeleteModel` → `est_supprime` / `date_suppression` + `.supprimer()` / `.restaurer()`.
- `SoftDeleteQuerySet` → `.vivants()` / `.supprimes()`.
- `CoordonneesMixin` → `latitude` / `longitude` + `est_geolocalise`. Les coordonnées sont **fournies par le composant carte** côté front (point sélectionné) ; le serveur ne fait **aucun calcul géométrique**, il stocke et restitue.

---

## 🔐 Authentification JWT

### Configuration (`settings.py`)

| Paramètre | Valeur dev | Description |
|---|---|---|
| `JWT_ACCESS_MINUTES` | `15` | Durée du token d'accès |
| `JWT_REFRESH_DAYS` | `7` | Durée du refresh token |
| `ROTATE_REFRESH_TOKENS` | `True` | Nouveau refresh token à chaque utilisation |
| `BLACKLIST_AFTER_ROTATION` | `True` | L'ancien refresh est blacklisté |
| `JWT_SIGNING_KEY` | `SECRET_KEY` | Clé de signature (overrider en prod via `.env`) |

Les valeurs sont lisibles depuis des **variables d'environnement** (pratique pour la prod sans modifier `settings.py`).

### Endpoints

| Méthode | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | ❌ | Création de compte → user + tokens |
| `POST` | `/api/auth/login` | ❌ | Connexion → user + tokens |
| `POST` | `/api/auth/refresh` | ❌ | Rafraîchir les tokens (rotation) |
| `GET` | `/api/auth/me` | ✅ JWT | Profil de l'utilisateur connecté |

### Flux JWT

```
1. POST /api/auth/register → { user, access, refresh }
2. POST /api/auth/login    → { user, access, refresh }
3. GET  /api/auth/me       Authorization: Bearer <access>
4. POST /api/auth/refresh  → { access, refresh }  (nouveaux tokens)
```

> ✅ Endpoints implémentés et testés (register, login, refresh, me + cas d'erreur 401/409).

---

## 👤 Modèle Utilisateur

**`Utilisateur`** étend `AbstractBaseUser` + `PermissionsMixin` + `SoftDeleteModel`.

On garde gratuitement : hashing du mot de passe, `is_staff`, `is_superuser`, permissions, `last_login` — plus l'audit et le soft delete mutualisés via `shared/`.

### Champs

| Champ | Type | Description |
|---|---|---|
| `email` | `EmailField` (unique) | **Identifiant de connexion** (pas de username) |
| `nom` | `CharField(150)` | Nom de famille |
| `prenom` | `CharField(150)` | Prénom |
| `telephone` | `CharField(20)` | Numéro de téléphone |
| `photo_profil` | `URLField` | Avatar |
| `role` | `CharField(choices)` | `CLIENT` / `VENDEUR` / `LIVREUR` / `ADMIN` |
| `is_active` | `BooleanField` | Compte actif |
| `is_staff` | `BooleanField` | Accès admin Django |
| `date_creation` | `DateTimeField` | Auto (hérité de `TimeStampedModel`) |
| `date_mise_a_jour` | `DateTimeField` | Auto (hérité de `TimeStampedModel`) |
| `est_supprime` | `BooleanField` | Soft delete (hérité de `SoftDeleteModel`) |
| `date_suppression` | `DateTimeField` | Date de suppression logique |

### Propriétés & manager

```python
utilisateur.is_client          # → True si role == CLIENT
utilisateur.is_vendeur         # → True si role == VENDEUR
utilisateur.is_livreur         # → True si role == LIVREUR
Utilisateur.objects.vivants()  # → QuerySet des comptes non supprimés
```

### Schémas Pydantic associés

| Schéma | Usage |
|---|---|
| `RegisterIn` | Payload d'inscription (email, password, nom, prenom, telephone, role) |
| `LoginIn` | Payload de connexion (`identifiant` = email **ou** téléphone, password) |
| `RefreshIn` | Payload de refresh (refresh token) |
| `UserOut` | Réponse publique (id, email, nom, prenom, role, dates…) |
| `TokenOut` | Paire de tokens (access + refresh) |
| `AuthResponseOut` | Réponse complète (user + tokens) |

---

## 🔧 Commandes utiles

```bash
# Vérifier la config
python manage.py check

# Créer une migration
python manage.py makemigrations users

# Appliquer les migrations
python manage.py migrate

# Shell Django
python manage.py shell

# Lancer sur un port spécifique
python manage.py runserver 127.0.0.1:8765

# Créer un superuser (interactif)
python manage.py createsuperuser
```

---

## 🔮 Modules à implémenter

D'après le [diagramme de classes](../conception.html) :

| Module | Entités | Statut |
|---|---|---|
| `shared` | TimeStampedModel, SoftDeleteModel, CoordonneesMixin, ApiResponse | ✅ Mixins + enveloppe API |
| `users` | Utilisateur, RoleUtilisateur | ✅ Modèle + Admin + Schemas |
| `auth` | JWT (register, login email/tél, refresh, me) | ✅ Implémenté + testé (17) |
| `places` | EmplacementMarché, Magasin, CentreCommercial | ✅ CRUD + validation + tests (15) |
| `catalog` | Produit, MediaProduit, CategorieProduit, EtatStock | ✅ CRUD + médias + tests (11) |
| `cart` | Panier, LignePanier | ✅ Panier 1↔1 user, prix live, tests (9) |
| `orders` | Commande, LigneCommande, AdresseLivraison, HistoriqueVente | ✅ Snapshots prix/addr, statuts, tests (12) |
| **`payments`** | **Paiement (Mobile Money, Espèces, Carte)** | **🔨 Prochaine étape** |
| `delivery` | Livraison, SuiviLivraison | ⬜ |
| `reviews` | AvisMagasin, AvisProduit | ⬜ |
| `favorites` | FavoriMagasin, FavoriProduit | ⬜ |
| `promotions` | Promotion | ⬜ |
| `notifications` | Notification | ⬜ |
| `moderation` | Signalement, ActionAdministrateur | ⬜ |
| `users` (suite) | Livreur, AdresseLivraison | ⬜ |

> **Total : 64 tests** verts (17 users + 15 places + 11 catalog + 9 cart + 12 orders).

---

## 🚧 Prochaine étape — module `payments`

Consommateur de `Commande`. Gère les tentatives de paiement :

```
catalog(Produit) ✅ → cart(Panier, LignePanier) ✅ → orders(Commande) ✅ → payments → delivery
```

- **`Paiement`** : 1 commande → 0..* paiements (MOBILE_MONEY, ESPECES, CARTE_BANCAIRE).
- **Statuts** : EN_ATTENTE → VALIDE (succès) ou ECHOUE (retry possible) → REMBOURSE.
- Logique : créer tentative, marquer commande confirmée si succès, rembourser.
- Même patron : fat models + services + router enveloppé + tests.

---

## 📡 Endpoints API avec exemples

### Auth (`/api/auth`)

#### `POST /api/auth/register` — Création de compte

**Requête :**
```json
{
  "email": "alice@example.com",
  "password": "SecurePass123!",
  "nom": "Dupont",
  "prenom": "Alice",
  "telephone": "+261340000001",
  "role": "CLIENT"
}
```

**Réponse 201 (Succès) :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T12:30:00Z",
  "data": {
    "user": {
      "id": 1,
      "email": "alice@example.com",
      "nom": "Dupont",
      "prenom": "Alice",
      "telephone": "+261340000001",
      "role": "CLIENT",
      "date_creation": "2026-06-24T12:30:00Z"
    },
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
  },
  "message": null,
  "error": null,
  "meta": null
}
```

**Réponse 409 (Email existe) :**
```json
{
  "success": false,
  "timestamp": "2026-06-24T12:31:00Z",
  "data": null,
  "message": "Un utilisateur avec cet email existe déjà.",
  "error": {
    "code": "CONFLICT",
    "message": "Un utilisateur avec cet email existe déjà.",
    "details": null
  },
  "meta": null
}
```

#### `POST /api/auth/login` — Connexion

**Requête :**
```json
{
  "identifiant": "alice@example.com",
  "password": "SecurePass123!"
}
```

**Réponse 200 (Succès) :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T12:35:00Z",
  "data": {
    "user": {
      "id": 1,
      "email": "alice@example.com",
      "nom": "Dupont",
      "prenom": "Alice",
      "telephone": "+261340000001",
      "role": "CLIENT"
    },
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
  },
  "message": null,
  "error": null,
  "meta": null
}
```

**Réponse 401 (Identifiants invalides) :**
```json
{
  "success": false,
  "timestamp": "2026-06-24T12:36:00Z",
  "data": null,
  "message": "Email ou mot de passe incorrect.",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Email ou mot de passe incorrect.",
    "details": null
  },
  "meta": null
}
```

#### `GET /api/auth/me` — Profil utilisateur connecté

**Réponse 200 (Succès) :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T12:40:00Z",
  "data": {
    "id": 1,
    "email": "alice@example.com",
    "nom": "Dupont",
    "prenom": "Alice",
    "telephone": "+261340000001",
    "role": "CLIENT",
    "date_creation": "2026-06-24T12:30:00Z"
  },
  "message": null,
  "error": null,
  "meta": null
}
```

---

### Places (`/api/places`)

#### `GET /api/places/magasins` — Lister magasins

**Réponse 200 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T13:00:00Z",
  "data": [
    {
      "id": 1,
      "nom": "Chez Rakoto",
      "description": "Épicerie générale",
      "adresse": "Rue de la Paix, Tana",
      "categorie": "ALIMENTATION",
      "est_ouvert": true,
      "est_valide": true,
      "date_creation": "2026-06-20T10:00:00Z"
    },
    {
      "id": 2,
      "nom": "Fashion District",
      "description": "Vêtements premium",
      "adresse": "Avenue de l'Indépendance",
      "categorie": "VETEMENTS",
      "est_ouvert": false,
      "est_valide": true,
      "date_creation": "2026-06-19T14:30:00Z"
    }
  ],
  "message": null,
  "error": null,
  "meta": {
    "total": 2
  }
}
```

#### `POST /api/places/magasins` — Créer magasin

**Requête :**
```json
{
  "nom": "Mon Supermarché",
  "description": "Produits variés",
  "centre_commercial_id": null,
  "categorie": "ALIMENTATION",
  "etage": "RDC",
  "numero_local": "15",
  "horaires_ouverture": {
    "1": [["09:00", "18:00"]],
    "2": [["09:00", "18:00"]],
    "3": [["09:00", "18:00"]],
    "4": [["09:00", "18:00"]],
    "5": [["09:00", "18:00"]],
    "6": [["10:00", "16:00"]],
    "7": []
  }
}
```

**Réponse 201 (Succès) :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T13:05:00Z",
  "data": {
    "id": 3,
    "nom": "Mon Supermarché",
    "description": "Produits variés",
    "categorie": "ALIMENTATION",
    "est_ouvert": true,
    "est_valide": false,
    "date_creation": "2026-06-24T13:05:00Z"
  },
  "message": "Magasin créé.",
  "error": null,
  "meta": null
}
```

**Réponse 403 (Pas vendeur) :**
```json
{
  "success": false,
  "timestamp": "2026-06-24T13:06:00Z",
  "data": null,
  "message": "Seul un vendeur peut créer un magasin.",
  "error": {
    "code": "FORBIDDEN",
    "message": "Seul un vendeur peut créer un magasin.",
    "details": null
  },
  "meta": null
}
```

---

### Catalog (`/api/catalog`)

#### `GET /api/catalog/produits?magasin_id=1` — Lister produits

**Réponse 200 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T13:30:00Z",
  "data": [
    {
      "id": 1,
      "nom": "Riz importé 5kg",
      "description": "Riz blanc de qualité premium",
      "categorie": "ALIMENTATION",
      "prix_mga": 15000,
      "quantite": 42,
      "etat_stock": "EN_STOCK",
      "est_disponible": true,
      "est_actif": true,
      "date_creation": "2026-06-22T10:00:00Z"
    },
    {
      "id": 2,
      "nom": "Sucre 2kg",
      "description": "Sucre blanc cristallisé",
      "categorie": "ALIMENTATION",
      "prix_mga": 3500,
      "quantite": 3,
      "etat_stock": "STOCK_FAIBLE",
      "est_disponible": true,
      "est_actif": true,
      "date_creation": "2026-06-21T15:20:00Z"
    }
  ],
  "message": null,
  "error": null,
  "meta": {
    "total": 2
  }
}
```

#### `POST /api/catalog/produits` — Créer produit

**Requête :**
```json
{
  "magasin_id": 1,
  "nom": "Huile de tournesol 1L",
  "description": "Huile de cuisson pure",
  "categorie": "ALIMENTATION",
  "prix_mga": 8500,
  "quantite": 25
}
```

**Réponse 201 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T13:35:00Z",
  "data": {
    "id": 3,
    "nom": "Huile de tournesol 1L",
    "description": "Huile de cuisson pure",
    "categorie": "ALIMENTATION",
    "prix_mga": 8500,
    "quantite": 25,
    "etat_stock": "EN_STOCK",
    "est_disponible": true,
    "est_actif": true,
    "date_creation": "2026-06-24T13:35:00Z"
  },
  "message": "Produit créé.",
  "error": null,
  "meta": null
}
```

#### `GET /api/catalog/produits/1/medias` — Galerie photos

**Réponse 200 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T13:40:00Z",
  "data": [
    {
      "id": 1,
      "produit_id": 1,
      "url_photo": "https://cdn.example.com/riz-1.jpg",
      "legende": "Vue avant du paquet",
      "ordre": 1,
      "date_creation": "2026-06-22T10:15:00Z"
    },
    {
      "id": 2,
      "produit_id": 1,
      "url_photo": "https://cdn.example.com/riz-2.jpg",
      "legende": "Détail du riz",
      "ordre": 2,
      "date_creation": "2026-06-22T10:16:00Z"
    }
  ],
  "message": null,
  "error": null,
  "meta": {
    "total": 2
  }
}
```

---

### Cart (`/api`)

#### `GET /api/panier` — Consulter panier

**Réponse 200 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T14:00:00Z",
  "data": {
    "id": 5,
    "utilisateur_id": 1,
    "total": 25500,
    "nombre_articles": 2,
    "date_creation": "2026-06-24T13:50:00Z"
  },
  "message": null,
  "error": null,
  "meta": {
    "articles": [
      {
        "id": 1,
        "produit_id": 1,
        "quantite": 1,
        "sous_total": 15000,
        "date_creation": "2026-06-24T13:52:00Z"
      },
      {
        "id": 2,
        "produit_id": 3,
        "quantite": 2,
        "sous_total": 10500,
        "date_creation": "2026-06-24T13:55:00Z"
      }
    ]
  }
}
```

> ℹ️ Panier : entité unique en `data`, articles détaillés en `meta` pour contexte.

#### `POST /api/panier/articles` — Ajouter article

**Requête :**
```json
{
  "produit_id": 2,
  "quantite": 3
}
```

**Réponse 201 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T14:05:00Z",
  "data": {
    "id": 3,
    "produit_id": 2,
    "quantite": 3,
    "sous_total": 10500,
    "date_creation": "2026-06-24T14:05:00Z"
  },
  "message": "Article ajouté.",
  "error": null,
  "meta": null
}
```

**Réponse 400 (Stock insuffisant) :**
```json
{
  "success": false,
  "timestamp": "2026-06-24T14:06:00Z",
  "data": null,
  "message": "Stock insuffisant. Disponible : 3.",
  "error": {
    "code": "BAD_REQUEST",
    "message": "Stock insuffisant. Disponible : 3.",
    "details": null
  },
  "meta": null
}
```

#### `DELETE /api/panier/articles/1` — Retirer article

**Réponse 200 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T14:10:00Z",
  "data": null,
  "message": "Article retiré du panier.",
  "error": null,
  "meta": null
}
```

---

### Orders (`/api`)

#### `POST /api/adresses` — Créer adresse de livraison

**Requête :**
```json
{
  "adresse_complete": "123 Rue de Madagascar",
  "ville": "Antananarivo",
  "quartier": "Analakely",
  "code_postal": "101",
  "complement": "Appartement 5B",
  "telephone": "+261340000099",
  "est_par_defaut": true
}
```

**Réponse 201 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T14:30:00Z",
  "data": {
    "id": 1,
    "adresse_complete": "123 Rue de Madagascar",
    "ville": "Antananarivo",
    "quartier": "Analakely",
    "code_postal": "101",
    "complement": "Appartement 5B",
    "telephone": "+261340000099",
    "est_par_defaut": true,
    "date_creation": "2026-06-24T14:30:00Z"
  },
  "message": null,
  "error": null,
  "meta": null
}
```

#### `GET /api/adresses` — Lister adresses

**Réponse 200 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T14:32:00Z",
  "data": [
    {
      "id": 1,
      "adresse_complete": "123 Rue de Madagascar",
      "ville": "Antananarivo",
      "quartier": "Analakely",
      "code_postal": "101",
      "complement": "Appartement 5B",
      "telephone": "+261340000099",
      "est_par_defaut": true,
      "date_creation": "2026-06-24T14:30:00Z"
    },
    {
      "id": 2,
      "adresse_complete": "456 Avenue de l'Indépendance",
      "ville": "Antananarivo",
      "quartier": "Androhibe",
      "code_postal": "101",
      "complement": "Bureau 2",
      "telephone": "+261340000088",
      "est_par_defaut": false,
      "date_creation": "2026-06-23T16:20:00Z"
    }
  ],
  "message": null,
  "error": null,
  "meta": {
    "total": 2
  }
}
```

#### `POST /api/commandes` — Passer commande

**Requête :**
```json
{
  "adresse_id": 1
}
```

**Réponse 201 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T14:35:00Z",
  "data": {
    "id": 10,
    "utilisateur_id": 1,
    "statut": "EN_ATTENTE",
    "adresse_snapshot": "123 Rue de Madagascar, Antananarivo",
    "total_mga": 25500,
    "date_creation": "2026-06-24T14:35:00Z",
    "lignes": [
      {
        "id": 1,
        "nom_produit_snapshot": "Riz importé 5kg",
        "quantite": 1,
        "prix_unitaire_mga": 15000,
        "sous_total": 15000,
        "date_creation": "2026-06-24T14:35:00Z"
      },
      {
        "id": 2,
        "nom_produit_snapshot": "Huile de tournesol 1L",
        "quantite": 2,
        "prix_unitaire_mga": 5250,
        "sous_total": 10500,
        "date_creation": "2026-06-24T14:35:00Z"
      }
    ]
  },
  "message": "Commande créée.",
  "error": null,
  "meta": null
}
```

**Réponse 400 (Panier vide) :**
```json
{
  "success": false,
  "timestamp": "2026-06-24T14:36:00Z",
  "data": null,
  "message": "Le panier est vide.",
  "error": {
    "code": "BAD_REQUEST",
    "message": "Le panier est vide.",
    "details": null
  },
  "meta": null
}
```

#### `GET /api/commandes` — Lister commandes

**Réponse 200 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T14:40:00Z",
  "data": [
    {
      "id": 10,
      "utilisateur_id": 1,
      "statut": "EN_ATTENTE",
      "adresse_snapshot": "123 Rue de Madagascar, Antananarivo",
      "total_mga": 25500,
      "date_creation": "2026-06-24T14:35:00Z",
      "lignes": []
    },
    {
      "id": 9,
      "utilisateur_id": 1,
      "statut": "CONFIRMEE",
      "adresse_snapshot": "456 Avenue de l'Indépendance",
      "total_mga": 8500,
      "date_creation": "2026-06-23T10:00:00Z",
      "lignes": []
    }
  ],
  "message": null,
  "error": null,
  "meta": {
    "total": 2
  }
}
```

#### `POST /api/commandes/10/annuler` — Annuler commande

**Réponse 200 :**
```json
{
  "success": true,
  "timestamp": "2026-06-24T14:45:00Z",
  "data": {
    "id": 10,
    "utilisateur_id": 1,
    "statut": "ANNULEE",
    "adresse_snapshot": "123 Rue de Madagascar, Antananarivo",
    "total_mga": 25500,
    "date_creation": "2026-06-24T14:35:00Z",
    "lignes": []
  },
  "message": "Commande annulée.",
  "error": null,
  "meta": null
}
```

**Réponse 400 (Statut confirmé) :**
```json
{
  "success": false,
  "timestamp": "2026-06-24T14:46:00Z",
  "data": null,
  "message": "Seules les commandes en attente peuvent être annulées.",
  "error": {
    "code": "BAD_REQUEST",
    "message": "Seules les commandes en attente peuvent être annulées.",
    "details": null
  },
  "meta": null
}
```

---

### Format d'erreur standard

**401 UNAUTHORIZED** — Token expiré ou invalide :
```json
{
  "success": false,
  "timestamp": "2026-06-24T14:50:00Z",
  "data": null,
  "message": "Token invalide ou expiré.",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token invalide ou expiré.",
    "details": null
  },
  "meta": null
}
```

**403 FORBIDDEN** — Accès refusé :
```json
{
  "success": false,
  "timestamp": "2026-06-24T14:51:00Z",
  "data": null,
  "message": "Vous n'avez pas les permissions pour effectuer cette action.",
  "error": {
    "code": "FORBIDDEN",
    "message": "Vous n'avez pas les permissions pour effectuer cette action.",
    "details": null
  },
  "meta": null
}
```

**404 NOT_FOUND** — Ressource inexistante :
```json
{
  "success": false,
  "timestamp": "2026-06-24T14:52:00Z",
  "data": null,
  "message": "Ressource introuvable.",
  "error": {
    "code": "NOT_FOUND",
    "message": "Ressource introuvable.",
    "details": null
  },
  "meta": null
}
```

**422 VALIDATION_ERROR** — Données invalides :
```json
{
  "success": false,
  "timestamp": "2026-06-24T14:53:00Z",
  "data": null,
  "message": "Données invalides.",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Erreur de validation.",
    "details": {
      "email": ["Adresse e-mail invalide"],
      "password": ["Le mot de passe doit faire au moins 8 caractères"]
    }
  },
  "meta": null
}
```

**500 INTERNAL_ERROR** — Erreur serveur (détails masqués en production) :
```json
{
  "success": false,
  "timestamp": "2026-06-24T14:54:00Z",
  "data": null,
  "message": "Une erreur interne s'est produite. Veuillez réessayer.",
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Une erreur interne s'est produite. Veuillez réessayer.",
    "details": null
  },
  "meta": null
}
```

---

## 📄 Licence

Projet privé — Demondra.
