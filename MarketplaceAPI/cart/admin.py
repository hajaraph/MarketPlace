from django.contrib import admin

from cart.models import LignePanier, Panier


class LignePanierInline(admin.TabularInline):
    model = LignePanier
    extra = 0
    fields = ("produit", "quantite", "sous_total")
    readonly_fields = ("sous_total",)


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "date_creation", "total")
    search_fields = ("utilisateur__email",)
    readonly_fields = ("date_creation", "date_mise_a_jour")
    inlines = (LignePanierInline,)

    def total(self, obj):
        return f"{obj.calculer_total():.2f} MGA"
    total.short_description = "Total"
