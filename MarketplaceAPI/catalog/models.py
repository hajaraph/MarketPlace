"""
Catalogue : Produit & MediaProduit.

Un Magasin possède un catalogue de Produits ; chaque Produit a une galerie
de MediaProduit. `etat_stock` est dérivé automatiquement de `quantite` à
l'enregistrement (cohérence garantie), `est_disponible` est calculé.
"""
from __future__ import annotations

from django.db import models

from places.models import Magasin
from shared.models import SoftDeleteModel, SoftDeleteQuerySet

# En dessous (inclus) de ce seuil et > 0, le stock est jugé faible.
SEUIL_STOCK_FAIBLE = 5


class CategorieProduit(models.TextChoices):
    ALIMENTATION = "ALIMENTATION", "Alimentation"
    VETEMENTS = "VETEMENTS", "Vêtements"
    ELECTRONIQUE = "ELECTRONIQUE", "Électronique"
    ARTISANAT = "ARTISANAT", "Artisanat"
    BEAUTE = "BEAUTE", "Beauté"
    MAISON = "MAISON", "Maison"
    AUTRE = "AUTRE", "Autre"


class EtatStock(models.TextChoices):
    EN_STOCK = "EN_STOCK", "En stock"
    STOCK_FAIBLE = "STOCK_FAIBLE", "Stock faible"
    RUPTURE_STOCK = "RUPTURE_STOCK", "Rupture de stock"


class Produit(SoftDeleteModel):
    magasin = models.ForeignKey(
        Magasin, on_delete=models.CASCADE,
        related_name="produits", verbose_name="Magasin",
    )
    nom = models.CharField("Nom", max_length=200)
    description = models.TextField("Description", blank=True, default="")
    categorie = models.CharField(
        "Catégorie", max_length=20,
        choices=CategorieProduit.choices, default=CategorieProduit.AUTRE,
    )
    prix_mga = models.DecimalField("Prix (MGA)", max_digits=12, decimal_places=2)
    quantite = models.PositiveIntegerField("Quantité", default=0)
    etat_stock = models.CharField(
        "État du stock", max_length=20,
        choices=EtatStock.choices, default=EtatStock.RUPTURE_STOCK,
    )
    est_actif = models.BooleanField("Actif", default=True)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom

    def _etat_depuis_quantite(self) -> str:
        if self.quantite <= 0:
            return EtatStock.RUPTURE_STOCK
        if self.quantite <= SEUIL_STOCK_FAIBLE:
            return EtatStock.STOCK_FAIBLE
        return EtatStock.EN_STOCK

    def save(self, *args, **kwargs):
        # L'état du stock est toujours dérivé de la quantité (jamais saisi à la main).
        self.etat_stock = self._etat_depuis_quantite()
        super().save(*args, **kwargs)

    @property
    def est_disponible(self) -> bool:
        return self.est_actif and not self.est_supprime and self.quantite > 0


class MediaProduit(SoftDeleteModel):
    produit = models.ForeignKey(
        Produit, on_delete=models.CASCADE,
        related_name="medias", verbose_name="Produit",
    )
    url_photo = models.URLField("URL de la photo")
    legende = models.CharField("Légende", max_length=255, blank=True, default="")
    ordre = models.PositiveIntegerField("Ordre d'affichage", default=0)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        verbose_name = "Média produit"
        verbose_name_plural = "Médias produit"
        ordering = ["ordre", "date_creation"]

    def __str__(self) -> str:
        return f"{self.produit.nom} — média #{self.ordre}"
