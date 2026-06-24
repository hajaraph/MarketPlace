from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from shared.models import SoftDeleteModel, SoftDeleteQuerySet


class RoleUtilisateur(models.TextChoices):
    """Rôles fonctionnels de la marketplace."""
    CLIENT = "CLIENT", "Client"
    VENDEUR = "VENDEUR", "Vendeur"
    LIVREUR = "LIVREUR", "Livreur"
    ADMIN = "ADMIN", "Administrateur"


class UtilisateurManager(BaseUserManager.from_queryset(SoftDeleteQuerySet)):
    """
    Manager custom : obligatoire dès qu'on retire `username` du modèle User.
    Toutes les créations passent par ici pour garantir le hashage du mot de passe.
    Hérite de SoftDeleteQuerySet → expose `.vivants()` / `.supprimes()`.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire.")
        email = self.normalize_email(email)
        # Par défaut, un utilisateur créé via cette méthode est un CLIENT actif.
        extra_fields.setdefault("role", RoleUtilisateur.CLIENT)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # hash le mot de passe
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Création d'un admin Django (via `manage.py createsuperuser`)."""
        extra_fields.setdefault("role", RoleUtilisateur.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superuser doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin, SoftDeleteModel):
    """
    Utilisateur de la marketplace.

    Hérite d'AbstractBaseUser : on garde le hashing de mot de passe et last_login,
    mais on remplace `username` par `email` comme identifiant de connexion.
    Hérite de SoftDeleteModel : audit (dates) + suppression logique mutualisés.
    """

    # --- Identité ---
    email = models.EmailField("Adresse e-mail", unique=True)
    nom = models.CharField("Nom", max_length=150)
    prenom = models.CharField("Prénom", max_length=150)
    telephone = models.CharField("Téléphone", max_length=20, blank=True, default="")

    # --- Avatar (URL ou chemin, on gérera l'upload plus tard) ---
    photo_profil = models.URLField("Photo de profil", blank=True, default="")

    # --- Rôle métier ---
    role = models.CharField(
        "Rôle",
        max_length=10,
        choices=RoleUtilisateur.choices,
        default=RoleUtilisateur.CLIENT,
    )

    # --- État du compte ---
    is_active = models.BooleanField("Actif", default=True)
    is_staff = models.BooleanField("Accès admin Django", default=False)

    # --- Cycle de vie (date_creation/date_mise_a_jour/est_supprime/
    #     date_suppression hérités de SoftDeleteModel) ---

    # --- Authentification ---
    USERNAME_FIELD = "email"  # on se connecte avec l'email
    REQUIRED_FIELDS = ["nom", "prenom"]  # demandés par createsuperuser

    objects = UtilisateurManager()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"

    @property
    def is_client(self):
        return self.role == RoleUtilisateur.CLIENT

    @property
    def is_vendeur(self):
        return self.role == RoleUtilisateur.VENDEUR

    @property
    def is_livreur(self):
        return self.role == RoleUtilisateur.LIVREUR

