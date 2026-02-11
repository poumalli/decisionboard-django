-- Création de la base de données EcoDistribution OLTP
-- PostgreSQL 13+

-- Extension pour les UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- TABLES DE RÉFÉRENCE
-- =============================================

-- Familles de produits
CREATE TABLE T_FAMILLES_PRODUITS (
    id_famille SERIAL PRIMARY KEY,
    libelle_famille VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Entrepôts
CREATE TABLE T_ENTREPOTS (
    id_entrepot SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    adresse TEXT NOT NULL,
    code_postal VARCHAR(10),
    ville VARCHAR(50),
    superficie DECIMAL(10,2), -- en m²
    capacite_stockage DECIMAL(10,2), -- en m³
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transporteurs
CREATE TABLE T_TRANSPORTEURS (
    id_transporteur SERIAL PRIMARY KEY,
    raison_sociale VARCHAR(200) NOT NULL UNIQUE,
    contact VARCHAR(100),
    telephone VARCHAR(20),
    email VARCHAR(100),
    tarif_km DECIMAL(8,3),
    zones_couvertes TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Commerciaux
CREATE TABLE T_COMMERCIAUX (
    id_commercial SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telephone VARCHAR(20),
    date_embauche DATE,
    secteur_geographique VARCHAR(200),
    statut VARCHAR(20) DEFAULT 'actif',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- TABLES PRINCIPALES
-- =============================================

-- Fournisseurs
CREATE TABLE T_FOURNISSEURS (
    id_fournisseur SERIAL PRIMARY KEY,
    raison_sociale VARCHAR(200) NOT NULL,
    siret VARCHAR(14) UNIQUE,
    adresse TEXT,
    code_postal VARCHAR(10),
    ville VARCHAR(50),
    telephone VARCHAR(20),
    email VARCHAR(100),
    delai_livraison_standard INTEGER DEFAULT 7, -- en jours
    statut VARCHAR(20) DEFAULT 'actif',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clients
CREATE TABLE T_CLIENTS (
    id_client SERIAL PRIMARY KEY,
    raison_sociale VARCHAR(200) NOT NULL,
    siret VARCHAR(14) UNIQUE,
    secteur_activite VARCHAR(100),
    taille_entreprise VARCHAR(50), -- TPE/PME/ETI/GE
    adresse TEXT NOT NULL,
    code_postal VARCHAR(10),
    ville VARCHAR(50),
    telephone VARCHAR(20),
    email VARCHAR(100),
    date_creation DATE DEFAULT CURRENT_DATE,
    statut VARCHAR(20) DEFAULT 'actif',
    condition_paiement VARCHAR(50) DEFAULT '30 jours',
    remise_contractuelle DECIMAL(5,2) DEFAULT 0.00,
    id_commercial_affected INTEGER REFERENCES T_COMMERCIAUX(id_commercial),
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Produits
CREATE TABLE T_PRODUITS (
    id_produit SERIAL PRIMARY KEY,
    reference VARCHAR(50) NOT NULL UNIQUE,
    libelle VARCHAR(200) NOT NULL,
    id_famille_produit INTEGER REFERENCES T_FAMILLES_PRODUITS(id_famille),
    description TEXT,
    poids DECIMAL(8,3), -- en kg
    volume DECIMAL(8,3), -- en m³
    prix_achat_ht DECIMAL(10,2) NOT NULL,
    prix_vente_ht DECIMAL(10,2) NOT NULL,
    marge_theorique DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN prix_achat_ht > 0 THEN ((prix_vente_ht - prix_achat_ht) / prix_achat_ht) * 100
            ELSE 0 
        END
    ) STORED,
    seuil_alerte_stock INTEGER DEFAULT 10,
    delai_livraison_fournisseur INTEGER DEFAULT 7,
    id_fournisseur_principal INTEGER REFERENCES T_FOURNISSEURS(id_fournisseur),
    statut VARCHAR(20) DEFAULT 'actif',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stocks
CREATE TABLE T_STOCKS (
    id_stock SERIAL PRIMARY KEY,
    id_produit INTEGER NOT NULL REFERENCES T_PRODUITS(id_produit),
    id_entrepot INTEGER NOT NULL REFERENCES T_ENTREPOTS(id_entrepot),
    quantite_disponible INTEGER DEFAULT 0,
    quantite_reservee INTEGER DEFAULT 0,
    quantite_totale INTEGER GENERATED ALWAYS AS (quantite_disponible + quantite_reservee) STORED,
    seuil_min INTEGER DEFAULT 5,
    seuil_max INTEGER DEFAULT 100,
    date_derniere_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_produit, id_entrepot)
);

-- Mouvements de stocks
CREATE TABLE T_MOUVEMENTS_STOCKS (
    id_mouvement SERIAL PRIMARY KEY,
    id_stock INTEGER NOT NULL REFERENCES T_STOCKS(id_stock),
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('entree', 'sortie', 'transfert', 'ajustement')),
    quantite INTEGER NOT NULL,
    date_mouvement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_document_source INTEGER, -- Référence à commande, livraison, etc.
    type_document VARCHAR(50),
    motif TEXT,
    id_utilisateur INTEGER
);

-- Commandes clients
CREATE TABLE T_COMMANDES_CLIENTS (
    id_commande SERIAL PRIMARY KEY,
    numero_commande VARCHAR(50) UNIQUE NOT NULL,
    id_client INTEGER NOT NULL REFERENCES T_CLIENTS(id_client),
    date_commande DATE DEFAULT CURRENT_DATE,
    date_livraison_prevue DATE,
    date_livraison_reelle DATE,
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'confirmee', 'en_preparation', 'expediee', 'livree', 'annulee')),
    montant_total_ht DECIMAL(12,2) DEFAULT 0.00,
    montant_tva DECIMAL(12,2) DEFAULT 0.00,
    montant_total_ttc DECIMAL(12,2) DEFAULT 0.00,
    id_commercial INTEGER REFERENCES T_COMMERCIAUX(id_commercial),
    notes TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lignes de commande
CREATE TABLE T_LIGNES_COMMANDE (
    id_ligne SERIAL PRIMARY KEY,
    id_commande INTEGER NOT NULL REFERENCES T_COMMANDES_CLIENTS(id_commande) ON DELETE CASCADE,
    id_produit INTEGER NOT NULL REFERENCES T_PRODUITS(id_produit),
    quantite_commandee INTEGER NOT NULL CHECK (quantite_commandee > 0),
    prix_unitaire_ht DECIMAL(10,2) NOT NULL,
    remise_ligne DECIMAL(5,2) DEFAULT 0.00,
    montant_ligne_ht DECIMAL(12,2) GENERATED ALWAYS AS (
        quantite_commandee * prix_unitaire_ht * (1 - remise_ligne/100)
    ) STORED,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Factures
CREATE TABLE T_FACTURES (
    id_facture SERIAL PRIMARY KEY,
    numero_facture VARCHAR(50) UNIQUE NOT NULL,
    id_commande INTEGER NOT NULL REFERENCES T_COMMANDES_CLIENTS(id_commande),
    date_facture DATE DEFAULT CURRENT_DATE,
    date_echeance DATE,
    montant_ht DECIMAL(12,2) NOT NULL,
    montant_tva DECIMAL(12,2) NOT NULL,
    montant_ttc DECIMAL(12,2) NOT NULL,
    statut VARCHAR(20) DEFAULT 'emise' CHECK (statut IN ('emise', 'payee', 'en_retard', 'annulee')),
    date_paiement DATE,
    mode_paiement VARCHAR(50),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Livraisons
CREATE TABLE T_LIVRAISONS (
    id_livraison SERIAL PRIMARY KEY,
    id_commande INTEGER NOT NULL REFERENCES T_COMMANDES_CLIENTS(id_commande),
    id_transporteur INTEGER REFERENCES T_TRANSPORTEURS(id_transporteur),
    date_expedition DATE,
    date_livraison_effective DATE,
    cout_transport DECIMAL(8,2),
    statut VARCHAR(20) DEFAULT 'preparee' CHECK (statut IN ('preparee', 'expediee', 'livree', 'retournee')),
    numero_suivi VARCHAR(100),
    nom_destinataire VARCHAR(200),
    adresse_livraison TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEX
-- =============================================

-- Index sur les tables de référence
CREATE INDEX idx_familles_produits_libelle ON T_FAMILLES_PRODUITS(libelle_famille);
CREATE INDEX idx_entrepots_nom ON T_ENTREPOTS(nom);
CREATE INDEX idx_transporteurs_raison_sociale ON T_TRANSPORTEURS(raison_sociale);

-- Index sur les clients
CREATE INDEX idx_clients_raison_sociale ON T_CLIENTS(raison_sociale);
CREATE INDEX idx_clients_secteur ON T_CLIENTS(secteur_activite);
CREATE INDEX idx_clients_statut ON T_CLIENTS(statut);
CREATE INDEX idx_clients_commercial ON T_CLIENTS(id_commercial_affected);

-- Index sur les produits
CREATE INDEX idx_produits_reference ON T_PRODUITS(reference);
CREATE INDEX idx_produits_libelle ON T_PRODUITS(libelle);
CREATE INDEX idx_produits_famille ON T_PRODUITS(id_famille_produit);
CREATE INDEX idx_produits_fournisseur ON T_PRODUITS(id_fournisseur_principal);
CREATE INDEX idx_produits_statut ON T_PRODUITS(statut);

-- Index sur les stocks
CREATE INDEX idx_stocks_produit ON T_STOCKS(id_produit);
CREATE INDEX idx_stocks_entrepot ON T_STOCKS(id_entrepot);
CREATE INDEX idx_stocks_quantite ON T_STOCKS(quantite_disponible);

-- Index sur les mouvements
CREATE INDEX idx_mouvements_stock ON T_MOUVEMENTS_STOCKS(id_stock);
CREATE INDEX idx_mouvements_date ON T_MOUVEMENTS_STOCKS(date_mouvement);
CREATE INDEX idx_mouvements_type ON T_MOUVEMENTS_STOCKS(type_mouvement);

-- Index sur les commandes
CREATE INDEX idx_commandes_numero ON T_COMMANDES_CLIENTS(numero_commande);
CREATE INDEX idx_commandes_client ON T_COMMANDES_CLIENTS(id_client);
CREATE INDEX idx_commandes_date ON T_COMMANDES_CLIENTS(date_commande);
CREATE INDEX idx_commandes_statut ON T_COMMANDES_CLIENTS(statut);
CREATE INDEX idx_commandes_commercial ON T_COMMANDES_CLIENTS(id_commercial);

-- Index sur les lignes de commande
CREATE INDEX idx_lignes_commande ON T_LIGNES_COMMANDE(id_commande);
CREATE INDEX idx_lignes_produit ON T_LIGNES_COMMANDE(id_produit);

-- Index sur les factures
CREATE INDEX idx_factures_numero ON T_FACTURES(numero_facture);
CREATE INDEX idx_factures_commande ON T_FACTURES(id_commande);
CREATE INDEX idx_factures_date ON T_FACTURES(date_facture);
CREATE INDEX idx_factures_statut ON T_FACTURES(statut);

-- Index sur les livraisons
CREATE INDEX idx_livraisons_commande ON T_LIVRAISONS(id_commande);
CREATE INDEX idx_livraisons_transporteur ON T_LIVRAISONS(id_transporteur);
CREATE INDEX idx_livraisons_date ON T_LIVRAISONS(date_expedition);
CREATE INDEX idx_livraisons_statut ON T_LIVRAISONS(statut);

-- =============================================
-- TRIGGERS
-- =============================================

-- Trigger pour mettre à jour les totaux de la commande
CREATE OR REPLACE FUNCTION update_commande_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE T_COMMANDES_CLIENTS 
    SET 
        montant_total_ht = (
            SELECT COALESCE(SUM(montant_ligne_ht), 0) 
            FROM T_LIGNES_COMMANDE 
            WHERE id_commande = NEW.id_commande
        ),
        montant_tva = (
            SELECT COALESCE(SUM(montant_ligne_ht) * 0.20, 0) 
            FROM T_LIGNES_COMMANDE 
            WHERE id_commande = NEW.id_commande
        ),
        montant_total_ttc = (
            SELECT COALESCE(SUM(montant_ligne_ht) * 1.20, 0) 
            FROM T_LIGNES_COMMANDE 
            WHERE id_commande = NEW.id_commande
        ),
        date_maj = CURRENT_TIMESTAMP
    WHERE id_commande = NEW.id_commande;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_commande_totals
    AFTER INSERT OR UPDATE OR DELETE ON T_LIGNES_COMMANDE
    FOR EACH ROW EXECUTE FUNCTION update_commande_totals();

-- Trigger pour mettre à jour la date de mise à jour des produits
CREATE OR REPLACE FUNCTION update_produit_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_maj = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_produit_timestamp
    BEFORE UPDATE ON T_PRODUITS
    FOR EACH ROW EXECUTE FUNCTION update_produit_timestamp();

-- Trigger pour mettre à jour les stocks après mouvement
CREATE OR REPLACE FUNCTION update_stock_after_movement()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE T_STOCKS 
    SET 
        quantite_disponible = CASE 
            WHEN NEW.type_mouvement IN ('entree', 'ajustement') THEN quantite_disponible + NEW.quantite
            WHEN NEW.type_mouvement = 'sortie' THEN quantite_disponible - NEW.quantite
            ELSE quantite_disponible
        END,
        date_derniere_maj = CURRENT_TIMESTAMP
    WHERE id_stock = NEW.id_stock;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_stock_movement
    AFTER INSERT ON T_MOUVEMENTS_STOCKS
    FOR EACH ROW EXECUTE FUNCTION update_stock_after_movement();

-- =============================================
-- VUES UTILES
-- =============================================

-- Vue synthétique des commandes avec détails client
CREATE VIEW V_COMMANDES_DETAIL AS
SELECT 
    c.id_commande,
    c.numero_commande,
    c.date_commande,
    c.statut,
    c.montant_total_ht,
    c.montant_total_ttc,
    cl.raison_sociale as client_raison_sociale,
    cl.secteur_activite,
    co.nom as commercial_nom,
    co.prenom as commercial_prenom
FROM T_COMMANDES_CLIENTS c
LEFT JOIN T_CLIENTS cl ON c.id_client = cl.id_client
LEFT JOIN T_COMMERCIAUX co ON c.id_commercial = co.id_commercial;

-- Vue état des stocks avec alertes
CREATE VIEW V_ETAT_STOCKS AS
SELECT 
    s.id_stock,
    p.reference,
    p.libelle as produit_libelle,
    e.nom as entrepot_nom,
    s.quantite_disponible,
    s.quantite_reservee,
    s.seuil_min,
    s.seuil_max,
    CASE 
        WHEN s.quantite_disponible <= s.seuil_min THEN 'ALERTE'
        WHEN s.quantite_disponible >= s.seuil_max THEN 'SURSTOCK'
        ELSE 'NORMAL'
    END as statut_stock
FROM T_STOCKS s
JOIN T_PRODUITS p ON s.id_produit = p.id_produit
JOIN T_ENTREPOTS e ON s.id_entrepot = e.id_entrepot;

-- Vue rentabilité par commande
CREATE VIEW V_RENTABILITE_COMMANDE AS
SELECT 
    c.id_commande,
    c.numero_commande,
    c.montant_total_ht as ca_ht,
    SUM(lc.quantite_commandee * p.prix_achat_ht) as cout_achat_ht,
    c.montant_total_ht - SUM(lc.quantite_commandee * p.prix_achat_ht) as marge_brute_ht,
    CASE 
        WHEN c.montant_total_ht > 0 THEN 
            ((c.montant_total_ht - SUM(lc.quantite_commandee * p.prix_achat_ht)) / c.montant_total_ht) * 100
        ELSE 0
    END as taux_marge_brute
FROM T_COMMANDES_CLIENTS c
JOIN T_LIGNES_COMMANDE lc ON c.id_commande = lc.id_commande
JOIN T_PRODUITS p ON lc.id_produit = p.id_produit
GROUP BY c.id_commande, c.numero_commande, c.montant_total_ht;
