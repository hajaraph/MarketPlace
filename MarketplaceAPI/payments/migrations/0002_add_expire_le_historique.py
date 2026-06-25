from datetime import timedelta

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def set_expire_le(apps, schema_editor):
    """Rétroactif : les paiements existants expirent 30 min après leur création."""
    Paiement = apps.get_model("payments", "Paiement")
    for p in Paiement.objects.all():
        p.expire_le = p.date_creation + timedelta(minutes=30)
        p.save(update_fields=["expire_le"])


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        # 1. Ajoute expire_le nullable d'abord
        migrations.AddField(
            model_name="paiement",
            name="expire_le",
            field=models.DateTimeField(
                blank=True, null=True,
                verbose_name="Expire le",
                help_text="Paiement automatiquement expiré après ce délai s'il reste EN_ATTENTE.",
            ),
        ),
        # 2. Rempli les lignes existantes
        migrations.RunPython(set_expire_le, migrations.RunPython.noop),
        # 3. Rend non-nullable
        migrations.AlterField(
            model_name="paiement",
            name="expire_le",
            field=models.DateTimeField(
                verbose_name="Expire le",
                help_text="Paiement automatiquement expiré après ce délai s'il reste EN_ATTENTE.",
            ),
        ),
        # 4. Ajoute EXPIRE aux choix du statut
        migrations.AlterField(
            model_name="paiement",
            name="statut",
            field=models.CharField(
                choices=[
                    ("EN_ATTENTE", "En attente"),
                    ("VALIDE", "Validé"),
                    ("ECHOUE", "Échoué"),
                    ("EXPIRE", "Expiré"),
                    ("REMBOURSE", "Remboursé"),
                ],
                default="EN_ATTENTE",
                max_length=20,
                verbose_name="Statut",
            ),
        ),
        # 5. Crée HistoriquePaiement
        migrations.CreateModel(
            name="HistoriquePaiement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_creation", models.DateTimeField(auto_now_add=True, verbose_name="Date de création")),
                ("date_mise_a_jour", models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")),
                ("statut_avant", models.CharField(max_length=20, verbose_name="Statut avant")),
                ("statut_apres", models.CharField(max_length=20, verbose_name="Statut après")),
                ("declencheur", models.CharField(
                    choices=[
                        ("UTILISATEUR", "Utilisateur"),
                        ("SYSTEME", "Système (expiration auto)"),
                        ("ADMIN", "Administrateur"),
                    ],
                    default="UTILISATEUR",
                    max_length=20,
                    verbose_name="Déclencheur",
                )),
                ("commentaire", models.TextField(blank=True, verbose_name="Commentaire")),
                ("paiement", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="historiques",
                    to="payments.paiement",
                    verbose_name="Paiement",
                )),
            ],
            options={
                "verbose_name": "Historique paiement",
                "verbose_name_plural": "Historiques paiements",
                "ordering": ["date_creation"],
            },
        ),
    ]
