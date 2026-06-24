"""
URL configuration for MarketplaceAPI project.

Le front Django admin reste accessible sur /admin.
L'API Ninja est montée sur /api (docs auto sur /api/docs).
"""
from django.contrib import admin
from django.urls import path

from api.ninja_api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
