"""
Management command : expire les paiements EN_ATTENTE dont le délai est dépassé.
Destiné à être appelé via cron (ex : toutes les 5 minutes).

    python manage.py expire_paiements
"""
from django.core.management.base import BaseCommand

from payments.services import expirer_paiements_expires


class Command(BaseCommand):
    help = "Expire les paiements EN_ATTENTE dont le délai est dépassé."

    def handle(self, *args, **options):
        count = expirer_paiements_expires()
        self.stdout.write(self.style.SUCCESS(f"{count} paiement(s) expiré(s)."))
