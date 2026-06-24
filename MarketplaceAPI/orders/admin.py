from django.contrib import admin

from orders.models import AdresseLivraison, Commande, HistoriqueVente, LigneCommande


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    fields = ("produit", "quantite", "prix_unitaire_mga", "sous_total")
    readonly_fields = ("sous_total",)


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ("id", "utilisateur", "statut", "total_mga", "date_creation")
    list_filter = ("statut", "date_creation")
    search_fields = ("utilisateur__email", "adresse_snapshot")
    readonly_fields = ("date_creation", "date_mise_a_jour", "total_mga")
    inlines = (LigneCommandeInline,)


@admin.register(AdresseLivraison)
class AdresseLivraisonAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "adresse_complete", "ville", "est_par_defaut")
    list_filter = ("est_par_defaut", "date_creation")
    search_fields = ("utilisateur__email", "adresse_complete")
    readonly_fields = ("date_creation", "date_mise_a_jour")


@admin.register(HistoriqueVente)
class HistoriqueVenteAdmin(admin.ModelAdmin):
    list_display = ("reference_commande", "nom_produit", "nom_magasin", "quantite_vendue", "date_creation")
    list_filter = ("date_creation",)
    search_fields = ("reference_commande", "nom_produit", "nom_magasin")
    readonly_fields = ("date_creation",)
