# Schéma OLTP - EcoDistribution

## Entités principales

### 1. Clients (T_CLIENTS)
- id_client (PK)
- raison_sociale
- siret
- secteur_activite
- taille_entreprise
- adresse_complete
- telephone
- email
- date_creation
- statut (actif/inactif)
- condition_paiement
- remise_contractuelle

### 2. Produits (T_PRODUITS)
- id_produit (PK)
- reference
- libelle
- id_famille_produit (FK)
- description
- poids
- volume
- prix_achat_ht
- prix_vente_ht
- marge_theorique
- seuil_alerte_stock
- delai_livraison_fournisseur
- statut (actif/inactif)

### 3. Familles produits (T_FAMILLES_PRODUITS)
- id_famille (PK)
- libelle_famille
- description

### 4. Fournisseurs (T_FOURNISSEURS)
- id_fournisseur (PK)
- raison_sociale
- siret
- adresse
- telephone
- email
- delai_livraison_standard
- statut

### 5. Commandes clients (T_COMMANDES_CLIENTS)
- id_commande (PK)
- id_client (FK)
- date_commande
- date_livraison_prevue
- date_livraison_reelle
- statut (en_attente/confirmee/expediee/livree/annulee)
- montant_total_ht
- montant_tva
- montant_total_ttc
- id_commercial (FK)

### 6. Lignes commande (T_LIGNES_COMMANDE)
- id_ligne (PK)
- id_commande (FK)
- id_produit (FK)
- quantite_commandee
- prix_unitaire_ht
- remise_ligne
- montant_ligne_ht

### 7. Stocks (T_STOCKS)
- id_stock (PK)
- id_produit (FK)
- id_entrepot (FK)
- quantite_disponible
- quantite_reservee
- date_derniere_maj
- seuil_min
- seuil_max

### 8. Mouvements stocks (T_MOUVEMENTS_STOCKS)
- id_mouvement (PK)
- id_stock (FK)
- type_mouvement (entree/sortie/transfert)
- quantite
- date_mouvement
- id_document_source (FK vers commande ou livraison)
- motif

### 9. Entrepôts (T_ENTREPOTS)
- id_entrepot (PK)
- nom
- adresse
- superficie
- capacite_stockage

### 10. Commerciaux (T_COMMERCIAUX)
- id_commercial (PK)
- nom
- prenom
- email
- telephone
- date_embauche
- secteur_geographique

### 11. Factures (T_FACTURES)
- id_facture (PK)
- id_commande (FK)
- date_facture
- date_echeance
- montant_ht
- montant_tva
- montant_ttc
- statut (emise/payee/en_retard)
- date_paiement

### 12. Livraisons (T_LIVRAISONS)
- id_livraison (PK)
- id_commande (FK)
- id_transporteur (FK)
- date_expedition
- date_livraison_effective
- cout_transport
- statut (preparee/expediee/livree)
- numero_suivi

### 13. Transporteurs (T_TRANSPORTEURS)
- id_transporteur (PK)
- raison_sociale
- contact
- tarif_km
- zones_couvertes

## Relations clés

- Un client peut avoir plusieurs commandes
- Une commande contient plusieurs lignes de commande
- Un produit peut être dans plusieurs lignes de commande
- Un produit peut être stocké dans plusieurs entrepôts
- Une commande génère une facture et une livraison
- Un commercial gère plusieurs clients/commandes

## Index recommandés

- idx_clients_secteur (secteur_activite)
- idx_produits_famille (id_famille_produit)
- idx_commandes_date (date_commande)
- idx_commandes_client (id_client)
- idx_stocks_produit (id_produit)
- idx_mouvements_date (date_mouvement)
