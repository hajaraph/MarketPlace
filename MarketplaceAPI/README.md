# Marketplace Maps — Backend API

Backend de la marketplace cartographique, construit avec **Django 6** + **Django Ninja** + **JWT**.

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
├── api/                     # ★ Couche API (Ninja)
│   ├── ninja_api.py         # Instance NinjaAPI — tous les routers sont enregistrés ici
│   └── routers/
│       ├── health.py        # GET /api/health
│       └── (auth.py …)      # Routers à venir (auth, catalog, orders, …)
│
├── users/                   # App Django : Utilisateurs
│   ├── models.py            # Utilisateur (AbstractBaseUser) + RoleUtilisateur
│   ├── admin.py             # Admin Django custom avec hash du mot de passe
│   ├── schemas.py           # Schémas Pydantic In/Out
│   ├── services.py           # (à venir) Logique métier register/login
│   ├── auth.py              # (à venir) Authenticateur JWT Bearer
│   └── migrations/
│
├── venv/                    # Environnement virtuel Python (non versionné)
├── db.sqlite3               # Base SQLite de dev (non versionnée)
├── requirements.txt          # Dépendances figées
├── manage.py
└── README.md
```

> **La structure DDD complète** (`domain/`, `application/`, `infrastructure/`, `presentation/`) sera ajoutée progressivement module par module. On commence petit, on grossit au besoin.

---

## ⚡ Stack technique

| Outil | Rôle |
|---|---|
| **Django 6.0.6** | Framework web |
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

### Endpoints prévus

| Méthode | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/` | ❌ | Création de compte |
| `POST` | `/api/auth/login/` | ❌ | Connexion → tokens |
| `POST` | `/api/auth/refresh/` | ❌ | Rafraîchir le token |
| `GET` | `/api/auth/me/` | ✅ JWT | Profil de l'utilisateur connecté |

### Flux JWT

```
1. POST /api/auth/register/ → { user, access, refresh }
2. POST /api/auth/login/    → { user, access, refresh }
3. GET  /api/auth/me/       Authorization: Bearer <access>
4. POST /api/auth/refresh/  → { access, refresh }  (nouveaux tokens)
```

> Les endpoints sont **en cours d'implémentation** — les schémas Pydantic (`users/schemas.py`) sont prêts.

---

## 👤 Modèle Utilisateur

**`Utilisateur`** étend `AbstractBaseUser` + `PermissionsMixin` de Django.

On garde gratuitement : hashing du mot de passe, `is_staff`, `is_superuser`, permissions, `last_login`.

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
| `date_creation` | `DateTimeField` | Auto (création) |
| `date_mise_a_jour` | `DateTimeField` | Auto (modification) |
| `est_supprime` | `BooleanField` | Soft delete |
| `date_suppression` | `DateTimeField` | Date de suppression logique |

### Propriétés pratiques

```python
utilisateur.is_client   # → True si role == CLIENT
utilisateur.is_vendeur  # → True si role == VENDEUR
utilisateur.is_livreur  # → True si role == LIVREUR
```

### Schémas Pydantic associés

| Schéma | Usage |
|---|---|
| `RegisterIn` | Payload d'inscription (email, password, nom, prenom, telephone, role) |
| `LoginIn` | Payload de connexion (email, password) |
| `RefreshIn` | Payload de refresh (refresh token) |
| `UserOut` | Réponse publique (id, email, nom, prenom, role, dates…) |
| `TokenOut` | Paire de tokens (access + refresh) |
| `AuthResponseOut` | Réponse complète (user + tokens) |

---

## 🏗️ Architecture cible (DDD)

La structure finale suivra l'architecture **Domain-Driven Design** en 3 couches (pas 4 — on supprime le DTO redondant) :

```
domain/           # ★ Cœur métier — ZÉRO dépendance Django
├── shared/       # Entity, AggregateRoot, PointGPS, Money
├── users/
├── places/       # EmplacementMarché, Magasin, CentreCommercial
├── catalog/      # Produit, MediaProduit
├── orders/
├── payments/
├── delivery/
├── reviews/
├── favorites/
├── promotions/
├── notifications/
└── moderation/

application/      # Use cases (orchestration)
├── users/        # RegisterUseCase, LoginUseCase, …
├── schemas.py    # Pydantic In/Out
└── …

infrastructure/   # Implémentation technique
├── persistence/
│   ├── mappers/  # ★ Unique point de mapping Entity ↔ Model
│   └── repos/    # Implémentation Django des repositories
├── external/     # Paiement, email, Maps API…
└── cache/        # Redis

api/              # Routers Ninja (minces, délèguent aux use cases)
apps/             # Django apps (persistance + admin + signals UNIQUEMENT)
```

**Dépendances strictes :**

```
api ──► application ──► domain ◄─── infrastructure
       (tous dépendent du domain, jamais l'inverse)
```

On ajoutera cette structure **module par module** au fur et à mesure de l'implémentation.

---

## 🔧 Commandes utiles

```bash
# Vérifier la config
python manage.py check

# Créer une migration
python manage.py makemigrations users

# Appliquer les migrations
python manage.py migrate

# Shell Django (avec coloration)
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
| `users` | Utilisateur, Livreur, AdresseLivraison | ✅ Modèle + Admin + Schemas |
| `auth` | JWT (register, login, refresh, me) | 🔨 Schemas prêts, endpoints en cours |
| `places` | EmplacementMarché, Magasin, CentreCommercial | ⬜ |
| `catalog` | Produit, MediaProduit, CategorieProduit | ⬜ |
| `cart` | Panier, LignePanier | ⬜ |
| `orders` | Commande, LigneCommande, HistoriqueVente | ⬜ |
| `payments` | Paiement (Mobile Money, Espèces, Carte) | ⬜ |
| `delivery` | Livraison, SuiviLivraison | ⬜ |
| `reviews` | AvisMagasin, AvisProduit | ⬜ |
| `favorites` | FavoriMagasin, FavoriProduit | ⬜ |
| `promotions` | Promotion | ⬜ |
| `notifications` | Notification | ⬜ |
| `moderation` | Signalement, ActionAdministrateur | ⬜ |

---

## 📄 Licence

Projet privé — Demondra.
