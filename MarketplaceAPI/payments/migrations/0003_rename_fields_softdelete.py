"""
Migration 0003 : aligne Paiement sur la conception.html
- mode → methode  (+ renomme ModePaiement → MethodePaiement côté choix)
- reference → reference_transaction
- TimeStampedModel → SoftDeleteModel (ajoute est_supprime + date_suppression)
- Ajoute date_paiement (DateTimeField nullable)
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0002_add_expire_le_historique"),
    ]

    operations = [
        # 1. Renomme mode → methode
        migrations.RenameField(
            model_name="paiement",
            old_name="mode",
            new_name="methode",
        ),
        # 2. Renomme reference → reference_transaction
        migrations.RenameField(
            model_name="paiement",
            old_name="reference",
            new_name="reference_transaction",
        ),
        # 3. Mise à jour des choices sur methode
        migrations.AlterField(
            model_name="paiement",
            name="methode",
            field=models.CharField(
                choices=[
                    ("MOBILE_MONEY", "Mobile Money"),
                    ("ESPECES", "Espèces"),
                    ("CARTE_BANCAIRE", "Carte bancaire"),
                ],
                max_length=20,
                verbose_name="Méthode de paiement",
            ),
        ),
        # 4. Ajoute est_supprime (SoftDeleteModel)
        migrations.AddField(
            model_name="paiement",
            name="est_supprime",
            field=models.BooleanField(default=False, verbose_name="Supprimé"),
        ),
        # 5. Ajoute date_suppression (SoftDeleteModel)
        migrations.AddField(
            model_name="paiement",
            name="date_suppression",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Date de suppression"
            ),
        ),
        # 6. Ajoute date_paiement
        migrations.AddField(
            model_name="paiement",
            name="date_paiement",
            field=models.DateTimeField(
                blank=True, null=True,
                verbose_name="Date de paiement",
                help_text="Renseigné à la validation effective du paiement.",
            ),
        ),
    ]
