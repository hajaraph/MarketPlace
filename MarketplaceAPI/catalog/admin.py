from django.contrib import admin

from catalog.models import MediaProduit, Produit


class MediaProduitInline(admin.TabularInline):
    model = MediaProduit
    extra = 1
    fields = ("url_photo", "legende", "ordre", "est_supprime")


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("nom", "magasin", "categorie", "prix_mga",
                    "quantite", "etat_stock", "est_actif", "date_creation")
    list_filter = ("categorie", "etat_stock", "est_actif", "est_supprime")
    search_fields = ("nom", "magasin__nom")
    autocomplete_fields = ("magasin",)
    readonly_fields = ("etat_stock", "date_creation", "date_mise_a_jour")
    inlines = (MediaProduitInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(est_supprime=False)
