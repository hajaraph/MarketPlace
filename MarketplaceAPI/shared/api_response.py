"""
Réponses API standardisées — version Django Ninja (pas DRF).

Toutes les réponses suivent la même enveloppe :

    {
        "success": bool,
        "timestamp": "ISO datetime",
        "data": {...} | null,
        "message": "string" | null,
        "error": { "message", "code", "details"? } | null,
        "meta": {...} | null
    }

- `Envelope` : schéma Pydantic exposé dans OpenAPI/Swagger (typage de la réponse).
- `ApiResponse` : fabrique de tuples `(http_status, dict)` — Ninja accepte ce
  format pour fixer le code HTTP tout en validant le corps contre `Envelope`.
- `register_exception_handlers(api)` : enveloppe TOUTE exception dans ce format,
  avec un handler précis par famille (auth/JWT, 404, 403, validation, conflit
  d'intégrité, 500) — fini les messages imprécis ou les dumps DRF bruts.
- `ensure_idempotent` : décorateur d'idempotence (header `X-Idempotency-Key`).
"""
from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Optional

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import (
    PermissionDenied,
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError
from django.http import Http404
from django.utils import timezone
from ninja import Schema
from ninja.errors import AuthenticationError, HttpError, ValidationError

logger = logging.getLogger("api")


# Codes d'erreur normalisés par statut HTTP (contrat stable côté front).
DEFAULT_ERROR_CODES: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "THROTTLED",
    500: "INTERNAL_ERROR",
}


# =========================================================
# Schéma d'enveloppe (documentation OpenAPI)
# =========================================================

class ErrorOut(Schema):
    """Bloc d'erreur typé (toujours présent en cas d'échec)."""
    message: str
    code: str
    details: Optional[Any] = None


class Envelope(Schema):
    """Enveloppe standard de toute réponse API."""
    success: bool
    timestamp: str
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[ErrorOut] = None
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
        # Code par défaut déduit du statut → jamais d'erreur sans code stable.
        code = code or DEFAULT_ERROR_CODES.get(http_status, "ERROR")
        error: dict[str, Any] = {"message": message, "code": code}
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
                     code: str = "INTERNAL_ERROR", details: Any = None) -> tuple[int, dict]:
        return ApiResponse.error(message, code=code, details=details, http_status=500)

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
# Extraction robuste des messages d'exceptions hétérogènes
# =========================================================

def _stringify(value: Any) -> str:
    """Aplati un détail d'erreur (str, ErrorDetail, list, dict) en une phrase."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        # DRF/ninja_jwt : { "detail": "...", "code": "...", "messages": [...] }
        if "detail" in value:
            return _stringify(value["detail"])
        return "; ".join(_stringify(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return "; ".join(_stringify(v) for v in value if _stringify(v))
    return str(value)


def _extract_code(exc: Any, default: str) -> str:
    """Récupère un code d'erreur stable depuis une exception DRF/ninja_jwt."""
    detail = getattr(exc, "detail", None)
    if isinstance(detail, dict):
        code = detail.get("code")
        if code is not None:
            return str(code).upper()
    code = getattr(detail, "code", None) or getattr(exc, "default_code", None)
    return str(code).upper() if code else default


# =========================================================
# Handlers d'erreur globaux — enveloppent toutes les exceptions
# =========================================================

def register_exception_handlers(api) -> None:
    """
    Branche un handler PRÉCIS par famille d'exception sur l'instance NinjaAPI.

    Ordre de spécificité (Ninja choisit le handler le plus dérivé dans la MRO) :
    APIException/Auth (JWT) → HttpError (métier) → Http404 / PermissionDenied /
    Validation (Django & Ninja) / IntegrityError → Exception (filet 500).
    """
    from ninja_extra.exceptions import APIException

    def respond(request, reponse: tuple[int, dict]):
        """Sérialise un `(status, body)` d'ApiResponse en réponse Ninja."""
        status, body = reponse
        return api.create_response(request, body, status=status)

    # --- Erreurs « simples » : message fixe ou str(exc), code/statut fixes ---
    # (exc_type, status, code, message_défaut, utiliser_str_exc)
    simples = [
        (AuthenticationError, 401, "UNAUTHORIZED", "Authentification requise.", False),
        (Http404, 404, "NOT_FOUND", "Ressource non trouvée.", True),
        (PermissionDenied, 403, "FORBIDDEN", "Accès refusé.", True),
    ]
    for exc_type, status, code, defaut, utiliser_str in simples:
        def faire_handler(status, code, defaut, utiliser_str):
            def handler(request, exc):
                message = (str(exc) if utiliser_str else "") or defaut
                return respond(request, ApiResponse.error(message, code=code, http_status=status))
            return handler
        api.exception_handler(exc_type)(faire_handler(status, code, defaut, utiliser_str))

    # --- Auth / JWT (ninja_jwt, ninja_extra) : str() dumpe le detail DRF -----
    @api.exception_handler(APIException)
    def _api_exception(request, exc: APIException):
        status = getattr(exc, "status_code", 401)
        message = _stringify(getattr(exc, "detail", None)) or "Authentification invalide."
        code = _extract_code(exc, DEFAULT_ERROR_CODES.get(status, "ERROR"))
        return respond(request, ApiResponse.error(message, code=code, http_status=status))

    # --- Erreurs métier explicites (HttpError levé dans les services) -------
    @api.exception_handler(HttpError)
    def _http_error(request, exc: HttpError):
        message = getattr(exc, "message", None) or str(exc)
        return respond(request, ApiResponse.error(message, http_status=exc.status_code))

    # --- Validation Ninja (payload non conforme au schéma) ------------------
    @api.exception_handler(ValidationError)
    def _ninja_validation(request, exc: ValidationError):
        return respond(request, ApiResponse.error(
            "Données invalides.", code="VALIDATION_ERROR",
            details=exc.errors, http_status=422))

    # --- Validation Django (model.full_clean / validators) ------------------
    @api.exception_handler(DjangoValidationError)
    def _django_validation(request, exc: DjangoValidationError):
        details = exc.message_dict if hasattr(exc, "error_dict") else exc.messages
        return respond(request, ApiResponse.error(
            "Données invalides.", code="VALIDATION_ERROR",
            details=details, http_status=422))

    # --- Conflit d'intégrité base (unicité, FK) -----------------------------
    @api.exception_handler(IntegrityError)
    def _integrity_error(request, exc: IntegrityError):
        logger.warning("IntegrityError sur %s : %s", request.path, exc)
        return respond(request, ApiResponse.error(
            "Conflit de données (contrainte d'unicité ou de référence).",
            code="CONFLICT", http_status=409))

    # --- Filet de sécurité : toute exception non prévue (500) ---------------
    @api.exception_handler(Exception)
    def _unhandled(request, exc: Exception):
        # On loggue TOUJOURS la stacktrace côté serveur ; on ne fuite jamais
        # les détails internes au client, sauf en DEBUG (dev).
        logger.exception("Exception non gérée sur %s", request.path)
        details = {"exception": type(exc).__name__, "detail": str(exc)} if settings.DEBUG else None
        return respond(request, ApiResponse.server_error(details=details))


# =========================================================
# Idempotence (header X-Idempotency-Key)
# =========================================================

# Méthodes pour lesquelles l'idempotence a du sens (les écritures).
_METHODES_IDEMPOTENTES = {"POST", "PUT", "PATCH", "DELETE"}


def ensure_idempotent(ttl: int = 3600):
    """
    Garantit qu'une requête d'écriture rejouée (même `X-Idempotency-Key`) ne
    s'exécute qu'une fois : la réponse est mise en cache `ttl` secondes et
    resservie à l'identique.

    - Sans clé, ou méthode de lecture → exécution normale (pas de cache).
    - La clé est namespacée par méthode + chemin → pas de collision entre
      endpoints qui partageraient une même clé.
    - Les erreurs serveur (>=500) ne sont jamais mises en cache.
    - Une panne du backend de cache ne casse jamais la requête (fail-open).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            key = request.headers.get("X-Idempotency-Key")
            if not key or request.method not in _METHODES_IDEMPOTENTES:
                return func(request, *args, **kwargs)

            cache_key = f"idempotent:{request.method}:{request.path}:{key}"
            try:
                cached = cache.get(cache_key)
            except Exception:  # cache indisponible → on n'empêche pas l'appel
                logger.warning("Cache indisponible (lecture idempotence)")
                cached = None
            if cached is not None:
                return cached["status"], cached["body"]

            result = func(request, *args, **kwargs)
            status, body = result if isinstance(result, tuple) else (200, result)
            if status < 500:
                try:
                    cache.set(cache_key, {"status": status, "body": body}, ttl)
                except Exception:
                    logger.warning("Cache indisponible (écriture idempotence)")
            return status, body
        return wrapper
    return decorator
