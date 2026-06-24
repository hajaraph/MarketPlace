"""
Réponses API standardisées — version Django Ninja (pas DRF).

Toutes les réponses suivent la même enveloppe :

    {
        "success": bool,
        "timestamp": "ISO datetime",
        "data": {...} | null,
        "message": "string" | null,
        "error": { "message", "code"?, "details"? } | null,
        "meta": {...} | null
    }

- `Envelope` : schéma Pydantic exposé dans OpenAPI/Swagger (typage de la réponse).
- `ApiResponse` : fabrique de tuples `(http_status, dict)` — Ninja accepte ce
  format pour fixer le code HTTP tout en validant le corps contre `Envelope`.
- `register_exception_handlers(api)` : enveloppe automatiquement les erreurs
  (HttpError métier, validation 422, exception 500) dans le même format.
- `ensure_idempotent` : décorateur d'idempotence (header `X-Idempotency-Key`).
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Optional

from django.core.cache import cache
from django.utils import timezone
from ninja import Schema
from ninja.errors import HttpError, ValidationError


# =========================================================
# Schéma d'enveloppe (documentation OpenAPI)
# =========================================================

class Envelope(Schema):
    """Enveloppe standard de toute réponse API."""
    success: bool
    timestamp: str
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[dict] = None
    meta: Optional[dict] = None


def _now() -> str:
    return timezone.now().isoformat()


# =========================================================
# Fabrique de réponses
# =========================================================

class ApiResponse:
    """Fabrique de réponses standardisées (retourne `(status, dict)`)."""

    # --- Succès -----------------------------------------------------------

    @staticmethod
    def success(data: Any = None, message: str | None = None,
                meta: dict | None = None, http_status: int = 200) -> tuple[int, dict]:
        body: dict[str, Any] = {"success": True, "timestamp": _now()}
        if data is not None:
            body["data"] = data
        if message:
            body["message"] = message
        if meta:
            body["meta"] = meta
        return http_status, body

    @staticmethod
    def created(data: Any = None, message: str = "Créé avec succès") -> tuple[int, dict]:
        return ApiResponse.success(data=data, message=message, http_status=201)

    # --- Erreurs ----------------------------------------------------------

    @staticmethod
    def error(message: str, code: str | None = None, details: Any = None,
              http_status: int = 400) -> tuple[int, dict]:
        error: dict[str, Any] = {"message": message}
        if code:
            error["code"] = code
        if details:
            error["details"] = details
        return http_status, {"success": False, "timestamp": _now(), "error": error}

    @staticmethod
    def not_found(message: str = "Ressource non trouvée",
                  code: str = "NOT_FOUND") -> tuple[int, dict]:
        return ApiResponse.error(message, code=code, http_status=404)

    @staticmethod
    def conflict(message: str = "Conflit détecté", code: str = "CONFLICT",
                 details: Any = None) -> tuple[int, dict]:
        return ApiResponse.error(message, code=code, details=details, http_status=409)

    @staticmethod
    def server_error(message: str = "Erreur interne du serveur",
                     code: str = "INTERNAL_ERROR") -> tuple[int, dict]:
        return ApiResponse.error(message, code=code, http_status=500)

    # --- Cas spécialisés --------------------------------------------------

    @staticmethod
    def sync_response(data: Any, server_time: str | None = None,
                      has_more: bool = False, next_cursor: str | None = None) -> tuple[int, dict]:
        sync = {"server_time": server_time or _now(), "has_more": has_more}
        if next_cursor:
            sync["next_cursor"] = next_cursor
        return 200, {"success": True, "timestamp": _now(), "data": data, "meta": {"sync": sync}}

    @staticmethod
    def batch_response(results: list[dict], success_count: int | None = None,
                       failure_count: int | None = None) -> tuple[int, dict]:
        if success_count is None:
            success_count = sum(1 for r in results if r.get("success", False))
        if failure_count is None:
            failure_count = len(results) - success_count
        return ApiResponse.success(
            data={"results": results},
            meta={"total": len(results),
                  "success_count": success_count,
                  "failure_count": failure_count},
        )


# =========================================================
# Handlers d'erreur globaux — enveloppent toutes les exceptions
# =========================================================

def register_exception_handlers(api) -> None:
    """Branche les handlers sur l'instance NinjaAPI pour uniformiser les erreurs."""

    @api.exception_handler(HttpError)
    def _http_error(request, exc: HttpError):
        message = getattr(exc, "message", None) or str(exc)
        status, body = ApiResponse.error(message, http_status=exc.status_code)
        return api.create_response(request, body, status=status)

    @api.exception_handler(ValidationError)
    def _validation_error(request, exc: ValidationError):
        status, body = ApiResponse.error(
            "Données invalides.", code="VALIDATION_ERROR",
            details=exc.errors, http_status=422,
        )
        return api.create_response(request, body, status=status)

    @api.exception_handler(Exception)
    def _unhandled(request, exc: Exception):
        status, body = ApiResponse.server_error()
        return api.create_response(request, body, status=status)


# =========================================================
# Idempotence (header X-Idempotency-Key)
# =========================================================

def ensure_idempotent(ttl: int = 3600):
    """
    Garantit qu'une requête rejouée (même `X-Idempotency-Key`) ne s'exécute
    qu'une fois : la réponse est mise en cache `ttl` secondes et resservie.

    Sans clé → exécution normale. Les erreurs serveur (>=500) ne sont pas cachées.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            key = request.headers.get("X-Idempotency-Key")
            if not key:
                return func(request, *args, **kwargs)

            cache_key = f"idempotent:{key}"
            cached = cache.get(cache_key)
            if cached is not None:
                return cached["status"], cached["body"]

            result = func(request, *args, **kwargs)
            status, body = result if isinstance(result, tuple) else (200, result)
            if status < 500:
                cache.set(cache_key, {"status": status, "body": body}, ttl)
            return status, body
        return wrapper
    return decorator
