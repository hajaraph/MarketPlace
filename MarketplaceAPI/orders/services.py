"""Use cases du module orders."""
from __future__ import annotations

from decimal import Decimal

from ninja.errors import HttpError

from cart.models import Panier
from catalog.models import Produit
from orders.models import (
    AdresseLivraison,
    Commande,
    HistoriqueVente,
    LigneCommande,
    StatutCommande,
)


def _get_adresse(adresse_id: int) -> AdresseLivraison:
    try:
        return AdresseLivraison.objects.vivants().get(pk=adresse_id)
    except AdresseLivraison.DoesNotExist:
        raise HttpError(404, "Adresse introuvable.")


def creer_adresse(user, data: dict) -> AdresseLivraison:
    """Crée une nouvelle adresse de livraison pour l'utilisateur."""
    adresse = AdresseLivraison.objects.create(
        utilisateur=user,
        adresse_complete=data["adresse_complete"],
        ville=data["ville"],
        quartier=data.get("quartier", ""),
        code_postal=data.get("code_postal", ""),
        complement=data.get("complement", ""),
        telephone=data["telephone"],
        est_par_defaut=data.get("est_par_defaut", False),
    )
    return adresse


def lister_adresses(user) -> list[AdresseLivraison]:
    """Liste les adresses de livraison de l'utilisateur."""
    return AdresseLivraison.objects.vivants().filter(utilisateur=user).all()


def supprimer_adresse(user, adresse_id: int) -> None:
    """Supprime une adresse de livraison."""
    adresse = _get_adresse(adresse_id)
    if adresse.utilisateur_id != user.id:
        raise HttpError(403, "Accès refusé.")
    adresse.supprimer()


def passer_commande(user, adresse_id: int | None = None) -> Commande:
    """
    Valide le panier → crée commande + snapshot + historique → vide panier.
    """
    panier = Panier.objects.get_or_create(utilisateur=user)[0]
    lignes_panier = panier.lignes.all()

    if not lignes_panier.exists():
        raise HttpError(400, "Le panier est vide.")

    # Récupère ou valide l'adresse
    adresse = None
    adresse_snapshot = ""
    if adresse_id:
        adresse = _get_adresse(adresse_id)
        if adresse.utilisateur_id != user.id:
            raise HttpError(403, "Accès refusé.")
        adresse_snapshot = f"{adresse.adresse_complete}, {adresse.ville}"

    # Vérifie le stock disponible
    for lp in lignes_panier:
        if lp.quantite > lp.produit.quantite:
            raise HttpError(400, f"Stock insuffisant pour {lp.produit.nom}.")

    # Crée la commande
    commande = Commande.objects.create(
        utilisateur=user,
        adresse=adresse,
        adresse_snapshot=adresse_snapshot,
        statut=StatutCommande.EN_ATTENTE,
    )

    # Crée les lignes commande + historiques de vente (par magasin)
    historiques_par_magasin = {}

    for lp in lignes_panier:
        produit = lp.produit
        prix = Decimal(str(produit.prix_mga))

        # Ligne commande
        LigneCommande.objects.create(
            commande=commande,
            produit=produit,
            quantite=lp.quantite,
            prix_unitaire_mga=prix,
            nom_produit_snapshot=produit.nom,
        )

        # Accumulateur historique par magasin
        magasin_id = produit.magasin_id
        if magasin_id not in historiques_par_magasin:
            historiques_par_magasin[magasin_id] = {
                "quantite": 0,
                "montant": Decimal("0"),
                "produits": [],
            }
        historiques_par_magasin[magasin_id]["quantite"] += lp.quantite
        historiques_par_magasin[magasin_id]["montant"] += (
            prix * Decimal(str(lp.quantite))
        )
        historiques_par_magasin[magasin_id]["produits"].append(
            (produit, lp.quantite, prix)
        )

    # Crée les historiques (une ligne par produit)
    for magasin_id, acc in historiques_par_magasin.items():
        magasin = acc["produits"][0][0].magasin  # On récupère le magasin
        for produit, quantite, prix in acc["produits"]:
            HistoriqueVente.objects.create(
                commande=commande,
                magasin=magasin,
                produit=produit,
                utilisateur=user,
                quantite_vendue=quantite,
                montant_total_mga=prix * Decimal(str(quantite)),
                nom_produit=produit.nom,
                prix_unitaire_mga=prix,
                nom_magasin=magasin.nom,
                nom_client=f"{user.prenom} {user.nom}",
                reference_commande=f"CMD-{commande.id:06d}",
            )

    # Calcule et sauvegarde le total
    commande.total_mga = commande.calculer_total()
    commande.save(update_fields=["total_mga"])

    # Vide le panier
    panier.vider()

    return commande


def lister_commandes(user) -> list[Commande]:
    """Liste les commandes de l'utilisateur."""
    return Commande.objects.vivants().filter(utilisateur=user).all()


def obtenir_commande(user, commande_id: int) -> Commande:
    """Récupère une commande (vérification propriétaire)."""
    try:
        commande = Commande.objects.vivants().get(pk=commande_id)
    except Commande.DoesNotExist:
        raise HttpError(404, "Commande introuvable.")
    if commande.utilisateur_id != user.id:
        raise HttpError(403, "Accès refusé.")
    return commande


def annuler_commande(user, commande_id: int) -> Commande:
    """Annule une commande (si elle est encore en attente)."""
    commande = obtenir_commande(user, commande_id)
    if commande.statut != StatutCommande.EN_ATTENTE:
        raise HttpError(400, "Seules les commandes en attente peuvent être annulées.")
    commande.annuler()
    return commande
