"""
Instance centrale de NinjaAPI.
Tous les routers y sont enregistrés ici, puis l'instance est montée
dans urls.py sous le préfixe /api.

Pour ajouter une nouvelle fonctionnalité (products, orders, ...):
  1. Créer api/routers/<module>.py avec un `router = Router()`
  2. L'importer ici et faire api.add_router("/<module>", router)
"""
from ninja import NinjaAPI

from api.routers import auth, health
from shared.api_response import register_exception_handlers

api = NinjaAPI(
    title="Marketplace Maps API",
    version="1.0.0",
    description="API REST de la marketplace cartographique.",
)

# --- Enveloppe standardisée des erreurs (HttpError, validation, 500) ---
register_exception_handlers(api)

# --- Enregistrement des routers ---
api.add_router("/", health.router)
api.add_router("/auth", auth.router)
