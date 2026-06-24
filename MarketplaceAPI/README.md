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
│       └── auth.py          # /api/auth/* (register, login, refresh, me)
│
├── shared/                  # ★ Noyau partagé (mixins réutilisables)
│   ├── models.py            # TimeStampedModel, SoftDeleteModel, SoftDeleteQuerySet
│   └── gps.py               # CoordonneesMixin (latitude/longitude)
│
├── users/                   # App Django : Utilisateurs
│   ├── models.py            # Utilisateur (AbstractBaseUser) + RoleUtilisateur
│   ├── services.py          # Use cases : register / login / refresh
│   ├── schemas.py           # Schémas Pydantic In/Out
│   ├── admin.py             # Admin Django custom
│   └── migrations/
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
| `LoginIn` | Payload de connexion (email, password) |
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
| `shared` | TimeStampedModel, SoftDeleteModel, CoordonneesMixin | ✅ Mixins de base |
| `users` | Utilisateur, RoleUtilisateur | ✅ Modèle + Admin + Schemas |
| `auth` | JWT (register, login, refresh, me) | ✅ Implémenté + testé |
| `users` (suite) | Livreur, AdresseLivraison | ⬜ |
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
