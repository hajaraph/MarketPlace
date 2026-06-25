from django.contrib import admin

from payments.models import HistoriquePaiement, Paiement


class HistoriquePaiementInline(admin.TabularInline):
    model = HistoriquePaiement
    extra = 0
    readonly_fields = ("statut_avant", "statut_apres", "declencheur", "commentaire", "date_creation")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("reference_transaction", "commande", "methode", "statut", "montant_mga", "date_paiement", "expire_le", "date_creation")
    list_filter = ("statut", "methode")
    search_fields = ("reference_transaction", "commande__id")
    readonly_fields = ("reference_transaction", "expire_le", "date_paiement", "date_creation", "date_mise_a_jour")
    inlines = [HistoriquePaiementInline]


@admin.register(HistoriquePaiement)
class HistoriquePaiementAdmin(admin.ModelAdmin):
    list_display = ("paiement", "statut_avant", "statut_apres", "declencheur", "date_creation")
    list_filter = ("declencheur", "statut_apres")
    search_fields = ("paiement__reference_transaction",)
    readonly_fields = ("paiement", "statut_avant", "statut_apres", "declencheur", "commentaire", "date_creation")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
