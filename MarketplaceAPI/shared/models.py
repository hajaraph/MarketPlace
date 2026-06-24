"""
Mixins de base réutilisés par toutes les entités de la marketplace.

- TimeStampedModel : audit création / mise à jour (auto).
- SoftDeleteModel  : suppression logique (est_supprime + date_suppression).

Note : on ne surcharge PAS le manager par défaut ici. Certains modèles
(ex. Utilisateur) ont leur propre manager obligatoire. Le filtrage des
enregistrements supprimés se fait explicitement via `Model.objects.vivants()`.
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):

    date_creation = models.DateTimeField("Date de création", auto_now_add=True)
    date_mise_a_jour = models.DateTimeField("Date de mise à jour", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):

    def vivants(self):
        return self.filter(est_supprime=False)

    def supprimes(self):
        return self.filter(est_supprime=True)


class SoftDeleteModel(TimeStampedModel):

    est_supprime = models.BooleanField("Supprimé", default=False)
    date_suppression = models.DateTimeField(
        "Date de suppression", null=True, blank=True
    )

    class Meta:
        abstract = True

    def supprimer(self) -> None:
        self.est_supprime = True
        self.date_suppression = timezone.now()
        self.save(update_fields=["est_supprime", "date_suppression"])

    def restaurer(self) -> None:
        self.est_supprime = False
        self.date_suppression = None
        self.save(update_fields=["est_supprime", "date_suppression"])
