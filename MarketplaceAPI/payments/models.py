from __future__ import annotations

from datetime import timedelta

from django.db import models
from django.utils import timezone

from orders.models import Commande
from shared.models import SoftDeleteModel, SoftDeleteQuerySet, TimeStampedModel

DUREE_EXPIRATION_MINUTES = 30


class MethodePaiement(models.TextChoices):
    MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
    ESPECES = "ESPECES", "Espèces"
    CARTE_BANCAIRE = "CARTE_BANCAIRE", "Carte bancaire"


class StatutPaiement(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", "En attente"
    VALIDE = "VALIDE", "Validé"
    ECHOUE = "ECHOUE", "Échoué"
    EXPIRE = "EXPIRE", "Expiré"
    REMBOURSE = "REMBOURSE", "Remboursé"


class Declencheur(models.TextChoices):
    UTILISATEUR = "UTILISATEUR", "Utilisateur"
    SYSTEME = "SYSTEME", "Système (expiration auto)"
    ADMIN = "ADMIN", "Administrateur"


class Paiement(SoftDeleteModel):
    objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    commande = models.ForeignKey(
        Commande, on_delete=models.PROTECT,
        related_name="paiements", verbose_name="Commande",
    )
    methode = models.CharField(
        "Méthode de paiement", max_length=20, choices=MethodePaiement.choices,
    )
    statut = models.CharField(
        "Statut", max_length=20,
        choices=StatutPaiement.choices,
        default=StatutPaiement.EN_ATTENTE,
    )
    montant_mga = models.DecimalField(
        "Montant (MGA)", max_digits=12, decimal_places=2,
    )
    reference_transaction = models.CharField(
        "Référence transaction", max_length=50, unique=True, blank=True,
    )
    note = models.TextField("Note", blank=True)
    expire_le = models.DateTimeField(
        "Expire le",
        help_text="Paiement automatiquement expiré après ce délai s'il reste EN_ATTENTE.",
    )
    date_paiement = models.DateTimeField(
        "Date de paiement", null=True, blank=True,
        help_text="Renseigné à la validation effective du paiement.",
    )

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ["-date_creation"]

    def __str__(self) -> str:
        return f"{self.reference_transaction} — {self.statut}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.expire_le:
            self.expire_le = timezone.now() + timedelta(minutes=DUREE_EXPIRATION_MINUTES)
        super().save(*args, **kwargs)
        if not self.reference_transaction:
            self.reference_transaction = f"PAY-{self.pk:06d}"
            self.__class__.objects.filter(pk=self.pk).update(
                reference_transaction=self.reference_transaction
            )

    @property
    def est_expire(self) -> bool:
        return self.statut == StatutPaiement.EN_ATTENTE and timezone.now() > self.expire_le

    def _changer_statut(self, nouveau: str, declencheur: str,
                        commentaire: str = "") -> None:
        ancien = self.statut
        self.statut = nouveau
        update_fields = ["statut", "date_mise_a_jour"]
        if nouveau == StatutPaiement.VALIDE:
            self.date_paiement = timezone.now()
            update_fields.append("date_paiement")
        self.save(update_fields=update_fields)
        HistoriquePaiement.objects.create(
            paiement=self,
            statut_avant=ancien,
            statut_apres=nouveau,
            declencheur=declencheur,
            commentaire=commentaire,
        )

    def valider(self, commentaire: str = "") -> None:
        self._changer_statut(StatutPaiement.VALIDE, Declencheur.UTILISATEUR, commentaire)

    def echouer(self, commentaire: str = "") -> None:
        self._changer_statut(StatutPaiement.ECHOUE, Declencheur.UTILISATEUR, commentaire)

    def expirer(self, commentaire: str = "Délai d'attente dépassé.") -> None:
        self._changer_statut(StatutPaiement.EXPIRE, Declencheur.SYSTEME, commentaire)

    def rembourser(self, commentaire: str = "", declencheur: str = Declencheur.ADMIN) -> None:
        self._changer_statut(StatutPaiement.REMBOURSE, declencheur, commentaire)


class HistoriquePaiement(TimeStampedModel):
    """Append-only — trace chaque transition de statut pour audit backoffice."""
    paiement = models.ForeignKey(
        Paiement, on_delete=models.PROTECT,
        related_name="historiques", verbose_name="Paiement",
    )
    statut_avant = models.CharField("Statut avant", max_length=20)
    statut_apres = models.CharField("Statut après", max_length=20)
    declencheur = models.CharField(
        "Déclencheur", max_length=20, choices=Declencheur.choices,
        default=Declencheur.UTILISATEUR,
    )
    commentaire = models.TextField("Commentaire", blank=True)

    class Meta:
        verbose_name = "Historique paiement"
        verbose_name_plural = "Historiques paiements"
        ordering = ["date_creation"]

    def __str__(self) -> str:
        return f"{self.paiement.reference_transaction} : {self.statut_avant} → {self.statut_apres}"
