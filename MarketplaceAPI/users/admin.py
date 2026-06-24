from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    """
    Admin custom : indispensable avec un AbstractBaseUser.
    - Hash le mot de passe à la création/modification
    - Organise les champs par groupes logiques
    """

    # Colonnes affichées dans la liste
    list_display = (
        "email",
        "nom",
        "prenom",
        "role",
        "is_active",
        "is_staff",
        "date_creation",
    )

    # Filtres latéraux
    list_filter = ("role", "is_active", "is_staff", "est_supprime")

    # Recherche
    search_fields = ("email", "nom", "prenom", "telephone")

    # Pagination
    list_per_page = 25

    # Ordre par défaut
    ordering = ("-date_creation",)

    # --- Réorganisation des formulaires d'édition ---
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Identité",
            {
                "fields": (
                    "nom",
                    "prenom",
                    "telephone",
                    "photo_profil",
                )
            },
        ),
        (
            "Rôle & permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Soft delete",
            {"fields": ("est_supprime", "date_suppression")},
        ),
        ("Dates importantes", {"fields": ("last_login", "date_creation", "date_mise_a_jour")}),
    )

    # --- Formulaire de création ---
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nom", "prenom", "role", "password1", "password2"),
            },
        ),
    )

    # Champs en lecture seule (auto-gérés)
    readonly_fields = ("date_creation", "date_mise_a_jour", "last_login")

    # Par défaut, on ne montre pas les comptes soft-deleted
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(est_supprime=False)


# Pour référence : raccourci vers les choix de rôle dans le reste de l'app
admin.site.empty_value_display = "—"
