"""
Coordonnées géographiques : stockage simple (latitude / longitude).

Les valeurs proviennent directement du composant carte côté front
(point sélectionné). On ne fait aucun calcul géométrique côté serveur —
juste la persistance et la restitution.

Implémentation : 2x FloatField. Si un jour des requêtes spatiales en SQL
(tri par proximité, rayon) deviennent nécessaires, on migrera vers
django-contrib-gis + PointField.
"""
from __future__ import annotations

from django.db import models


class CoordonneesMixin(models.Model):
    """Ajoute latitude/longitude optionnelles à un modèle."""

    latitude = models.FloatField("Latitude", null=True, blank=True)
    longitude = models.FloatField("Longitude", null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def est_geolocalise(self) -> bool:
        return self.latitude is not None and self.longitude is not None
