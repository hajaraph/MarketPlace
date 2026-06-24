"""
Router de santé de l'API.
Sert de validation minimale : si /api/health répond, Ninja est bien branché.
"""
from ninja import Router

router = Router(tags=["health"])


@router.get("/health")
def health_check(request):
    """Vérifie que l'API est en ligne."""
    return {"status": "ok", "service": "MarketplaceAPI"}
