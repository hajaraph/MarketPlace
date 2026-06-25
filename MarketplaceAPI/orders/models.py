"""
Commandes, adresses, historique de ventes.

Commande : snapshot figé du panier (prix, adresse, produit names).
LigneCommande : quantité + prix snapshot + nom snapshot.
HistoriqueVente : append-only reporting par magasin/produit/client.
AdresseLivraison : adresses réutilisables de l'utilisateur.
"""
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from catalog.models import Produit
from places.models import Magasin
from shared.gps import CoordonneesMixin
from shared.models import SoftDeleteModel, SoftDeleteQuerySet, TimeStampedModel


class StatutCommande(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", "En attente"
    CONFIRMEE = "CONFIRMEE", "Confirmée"
    PREPARATION = "PREPARATION", "Préparation"
    LIVRAISON_EN_COURS = "LIVRAISON_EN_COURS", "Livraison en cours"
    LIVREE = "LIVREE", "Livrée"
    ANNULEE = "ANNULEE", "Annulée"


class AdresseLivraison(SoftDeleteModel, CoordonneesMixin):
    """Adresse réutilisable de l'utilisateur (plusieurs par utilisateur)."""
    objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="adresses_livraison", verbose_name="Utilisateur",
    )
    adresse_complete = models.CharField("Adresse complète", max_length=255)
    ville = models.CharField("Ville", max_length=100)
    quartier = models.CharField("Quartier", max_length=100, blank=True)
    code_postal = models.CharField("Code postal", max_length=10, blank=True)
    complement = models.CharField("Complément", max_length=255, blank=True)
    telephone = models.CharField("Téléphone", max_length=20)
    est_par_defaut = models.BooleanField("Par défaut", default=False)

    class Meta:
        verbose_name = "Adresse de livraison"
        verbose_name_plural = "Adresses de livraison"
        ordering = ["-est_par_defaut", "-date_creation"]

    def __str__(self) -> str:
        return f"{self.adresse_complete}, {self.ville}"


class Commande(SoftDeleteModel):
    """Commande figée (snapshot des prix/adresse au moment de la création)."""
    objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="commandes", verbose_name="Utilisateur",
    )
    adresse = models.ForeignKey(
        AdresseLivraison, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+", verbose_name="Adresse",
    )
    adresse_snapshot = models.CharField(
        "Snapshot adresse", max_length=255, blank=True,
        help_text="Copie textuelle de l'adresse au moment de la création",
    )
    statut = models.CharField(
        "Statut",
        max_length=20,
        choices=StatutCommande.choices,
        default=StatutCommande.EN_ATTENTE,
    )
    total_mga = models.DecimalField(
        "Total (MGA)", max_digits=12, decimal_places=2, default=0,
    )

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ["-date_creation"]

    def __str__(self) -> str:
        return f"Commande #{self.id} — {self.utilisateur.email}"

    def calculer_total(self) -> Decimal:
        """Somme des sous-totaux des lignes."""
        return sum(
            Decimal(ligne.sous_total) for ligne in self.lignes.all()
        ) or Decimal("0")

    def annuler(self) -> None:
        """Passe la commande à ANNULEE."""
        self.statut = StatutCommande.ANNULEE
        self.save(update_fields=["statut", "date_mise_a_jour"])


class LigneCommande(TimeStampedModel):
    """Ligne de commande avec snapshots figés (prix + nom)."""
    commande = models.ForeignKey(
        Commande, on_delete=models.CASCADE,
        related_name="lignes", verbose_name="Commande",
    )
    produit = models.ForeignKey(
        Produit, on_delete=models.PROTECT,
        related_name="+", verbose_name="Produit",
    )
    quantite = models.PositiveIntegerField("Quantité")
    prix_unitaire_mga = models.DecimalField(
        "Prix unitaire (MGA)", max_digits=12, decimal_places=2,
    )
    nom_produit_snapshot = models.CharField(
        "Snapshot nom produit", max_length=255,
        help_text="Nom du produit au moment de la création",
    )

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
        ordering = ["date_creation"]

    def __str__(self) -> str:
        return f"{self.nom_produit_snapshot} x{self.quantite}"

    @property
    def sous_total(self) -> Decimal:
        """Quantité × prix unitaire figé."""
        return Decimal(self.quantite) * self.prix_unitaire_mga


class HistoriqueVente(TimeStampedModel):
    """
    Append-only : snapshot de vente à titre informatif/reporting.
    Ne se supprime jamais, même si produit/magasin/client est supprimé.
    """
    commande = models.ForeignKey(
        Commande, on_delete=models.PROTECT,
        related_name="historiques", verbose_name="Commande",
    )
    magasin = models.ForeignKey(
        Magasin, on_delete=models.PROTECT,
        related_name="+", verbose_name="Magasin",
    )
    produit = models.ForeignKey(
        Produit, on_delete=models.PROTECT,
        related_name="+", verbose_name="Produit",
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="+", verbose_name="Client",
    )
    quantite_vendue = models.PositiveIntegerField("Quantité vendue")
    montant_total_mga = models.DecimalField(
        "Montant total (MGA)", max_digits=12, decimal_places=2,
    )
    nom_produit = models.CharField("Nom produit", max_length=255)
    prix_unitaire_mga = models.DecimalField(
        "Prix unitaire (MGA)", max_digits=12, decimal_places=2,
    )
    nom_magasin = models.CharField("Nom magasin", max_length=255)
    nom_client = models.CharField("Nom client", max_length=255)
    reference_commande = models.CharField("Référence commande", max_length=50)

    class Meta:
        verbose_name = "Historique de vente"
        verbose_name_plural = "Historiques de vente"
        ordering = ["-date_creation"]

    def __str__(self) -> str:
        return f"{self.nom_produit} ({self.reference_commande})"
