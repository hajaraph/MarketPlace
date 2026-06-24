from django.contrib import admin

from places.models import CentreCommercial, Magasin


@admin.register(Magasin)
class MagasinAdmin(admin.ModelAdmin):
    list_display = ("nom", "categorie", "proprietaire", "centre_commercial",
                    "est_valide", "date_creation")
    list_filter = ("categorie", "est_valide", "est_supprime")
    search_fields = ("nom", "adresse", "proprietaire__email")
    autocomplete_fields = ("proprietaire", "centre_commercial")
    readonly_fields = ("date_creation", "date_mise_a_jour", "date_validation")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(est_supprime=False)


@admin.register(CentreCommercial)
class CentreCommercialAdmin(admin.ModelAdmin):
    list_display = ("nom", "nombre_etages", "parking_disponible",
                    "est_valide", "date_creation")
    list_filter = ("parking_disponible", "est_valide", "est_supprime")
    search_fields = ("nom", "adresse")
    readonly_fields = ("date_creation", "date_mise_a_jour", "date_validation")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(est_supprime=False)
