"""
Emplacements sur la carte : Magasin & CentreCommercial.

EmplacementMarche est une base ABSTRAITE (pas de table) : chaque sous-classe
concrète a sa propre table avec les champs communs factorisés. Cohérent avec
le diagramme de classes (héritage, pas de TypeEmplacement redondant).
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from shared.gps import CoordonneesMixin
from shared.models import SoftDeleteModel, SoftDeleteQuerySet


class CategorieMagasin(models.TextChoices):
    ALIMENTATION = "ALIMENTATION", "Alimentation"
    VETEMENTS = "VETEMENTS", "Vêtements"
    ELECTRONIQUE = "ELECTRONIQUE", "Électronique"
    RESTAURANT = "RESTAURANT", "Restaurant"
    PHARMACIE = "PHARMACIE", "Pharmacie"
    ARTISANAT = "ARTISANAT", "Artisanat"
    BEAUTE = "BEAUTE", "Beauté"
    MAISON = "MAISON", "Maison"
    AUTRE = "AUTRE", "Autre"


class EmplacementMarche(SoftDeleteModel, CoordonneesMixin):
    """
    Point sur la carte (abstrait). `localisation` = latitude/longitude
    (CoordonneesMixin). `est_ouvert` est CALCULÉ, jamais stocké.
    """

    nom = models.CharField("Nom", max_length=200)
    description = models.TextField("Description", blank=True, default="")
    banniere = models.URLField("Bannière", blank=True, default="")
    adresse = models.CharField("Adresse", max_length=255, blank=True, default="")

    # Horaires structurés : { "1".."7" (isoweekday) : [["08:00","18:00"], ...] }
    # Une clé absente ou une liste vide = fermé ce jour-là.
    horaires_ouverture = models.JSONField("Horaires d'ouverture", default=dict, blank=True)

    # Validation par un administrateur
    est_valide = models.BooleanField("Validé", default=False)
    date_validation = models.DateTimeField("Date de validation", null=True, blank=True)
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="%(class)ss_valides",
        verbose_name="Validé par",
    )

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom

    @property
    def est_ouvert(self) -> bool | None:
        """
        Déduit l'ouverture de `horaires_ouverture` à l'instant courant
        (fuseau du serveur). None si aucun horaire renseigné.
        """
        if not self.horaires_ouverture:
            return None
        maintenant = timezone.localtime()
        intervalles = self.horaires_ouverture.get(str(maintenant.isoweekday()), [])
        heure = maintenant.strftime("%H:%M")
        return any(
            ouverture <= heure <= fermeture for ouverture, fermeture in intervalles
        )

    def valider(self, par) -> None:
        """Validation administrateur : marque l'emplacement comme validé."""
        self.est_valide = True
        self.date_validation = timezone.now()
        self.valide_par = par
        self.save(update_fields=["est_valide", "date_validation", "valide_par"])


class CentreCommercial(EmplacementMarche):
    nombre_etages = models.PositiveIntegerField("Nombre d'étages", default=1)
    parking_disponible = models.BooleanField("Parking disponible", default=False)

    class Meta(EmplacementMarche.Meta):
        abstract = False
        verbose_name = "Centre commercial"
        verbose_name_plural = "Centres commerciaux"


class Magasin(EmplacementMarche):
    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="magasins",
        verbose_name="Propriétaire",
    )
    centre_commercial = models.ForeignKey(
        CentreCommercial,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="magasins",
        verbose_name="Centre commercial",
    )
    categorie = models.CharField(
        "Catégorie", max_length=20,
        choices=CategorieMagasin.choices, default=CategorieMagasin.AUTRE,
    )
    etage = models.CharField("Étage", max_length=20, blank=True, default="")
    numero_local = models.CharField("Numéro de local", max_length=20, blank=True, default="")

    class Meta(EmplacementMarche.Meta):
        abstract = False
        verbose_name = "Magasin"
        verbose_name_plural = "Magasins"
