"""
Panier (transitoire) : Panier + LignePanier.

Chaque utilisateur a UN panier. Les lignes contiennent une quantité +
une FK Produit. Le prix est LIVE (pas de snapshot) — on le cherche dans
le Produit au moment de l'affichage / calcul.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models

from catalog.models import Produit
from shared.models import TimeStampedModel


class Panier(TimeStampedModel):
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="panier", verbose_name="Utilisateur",
    )

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def __str__(self) -> str:
        return f"Panier de {self.utilisateur}"

    def calculer_total(self) -> float:
        """Somme (quantite * prix_live) de toutes les lignes."""
        return sum(ligne.sous_total for ligne in self.lignes.all())

    def vider(self) -> None:
        """Supprime tous les articles du panier."""
        self.lignes.all().delete()


class LignePanier(TimeStampedModel):
    panier = models.ForeignKey(
        Panier, on_delete=models.CASCADE,
        related_name="lignes", verbose_name="Panier",
    )
    produit = models.ForeignKey(
        Produit, on_delete=models.PROTECT,
        related_name="+", verbose_name="Produit",
    )
    quantite = models.PositiveIntegerField("Quantité", default=1)

    class Meta:
        verbose_name = "Ligne de panier"
        verbose_name_plural = "Lignes de panier"
        unique_together = ("panier", "produit")
        ordering = ["date_creation"]

    def __str__(self) -> str:
        return f"{self.produit.nom} x{self.quantite}"

    @property
    def sous_total(self) -> float:
        """Prix live × quantité."""
        return float(self.produit.prix_mga * self.quantite)
