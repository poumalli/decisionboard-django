-- Data Warehouse EcoDistribution - Schéma en étoile
-- PostgreSQL 13+

-- =============================================
-- CRÉATION DU SCHÉMA DW
-- =============================================

CREATE SCHEMA IF NOT EXISTS dw;

-- =============================================
-- DIMENSIONS
-- =============================================

-- Dimension Temps
CREATE TABLE dw.dim_temps (
    id_temps SERIAL PRIMARY KEY,
    date_complete DATE NOT NULL UNIQUE,
    annee INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    jour INTEGER NOT NULL,
    jour_semaine INTEGER NOT NULL,
    nom_jour VARCHAR(10) NOT NULL,
    nom_mois VARCHAR(20) NOT NULL,
    nom_trimestre VARCHAR(20) NOT NULL,
    semaine_annee INTEGER NOT NULL,
    est_jour_ferie BOOLEAN DEFAULT FALSE,
    est_weekend BOOLEAN DEFAULT FALSE,
    periode_mois VARCHAR(7) NOT NULL, -- YYYY-MM
    periode_trimestre VARCHAR(7) NOT NULL, -- YYYY-Q#
    periode_annee VARCHAR(4) NOT NULL -- YYYY
);

-- Dimension Client
CREATE TABLE dw.dim_client (
    id_client SERIAL PRIMARY KEY,
    id_client_source INTEGER NOT NULL, -- Référence à la table OLTP
    raison_sociale VARCHAR(200) NOT NULL,
    siret VARCHAR(14),
    secteur_activite VARCHAR(100),
    taille_entreprise VARCHAR(50),
    region VARCHAR(50),
    departement VARCHAR(50),
    code_postal VARCHAR(10),
    ville VARCHAR(50),
    condition_paiement VARCHAR(50),
    remise_contractuelle DECIMAL(5,2),
    date_creation DATE,
    statut VARCHAR(20),
    segment_client VARCHAR(50) GENERATED ALWAYS AS (
        CASE 
            WHEN taille_entreprise = 'TPE' THEN 'Petits comptes'
            WHEN taille_entreprise = 'PME' THEN 'Comptes moyens'
            WHEN taille_entreprise IN ('ETI', 'GE') THEN 'Grands comptes'
            ELSE 'Autres'
        END
    ) STORED,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension Produit
CREATE TABLE dw.dim_produit (
    id_produit SERIAL PRIMARY KEY,
    id_produit_source INTEGER NOT NULL, -- Référence à la table OLTP
    reference VARCHAR(50) NOT NULL,
    libelle VARCHAR(200) NOT NULL,
    famille_produit VARCHAR(100),
    sous_famille_produit VARCHAR(100),
    poids DECIMAL(8,3),
    volume DECIMAL(8,3),
    prix_achat_ht DECIMAL(10,2),
    prix_vente_ht DECIMAL(10,2),
    marge_theorique_pct DECIMAL(5,2),
    fournisseur_principal VARCHAR(200),
    delai_livraison_fournisseur INTEGER,
    statut VARCHAR(20),
    categorie_marge VARCHAR(50) GENERATED ALWAYS AS (
        CASE 
            WHEN marge_theorique_pct >= 50 THEN 'Très haute marge'
            WHEN marge_theorique_pct >= 30 THEN 'Haute marge'
            WHEN marge_theorique_pct >= 20 THEN 'Marge moyenne'
            WHEN marge_theorique_pct >= 10 THEN 'Faible marge'
            ELSE 'Très faible marge'
        END
    ) STORED,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension Commercial
CREATE TABLE dw.dim_commercial (
    id_commercial SERIAL PRIMARY KEY,
    id_commercial_source INTEGER NOT NULL, -- Référence à la table OLTP
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    nom_complet VARCHAR(101) GENERATED ALWAYS AS (prenom || ' ' || nom) STORED,
    email VARCHAR(100),
    telephone VARCHAR(20),
    date_embauche DATE,
    anciennete_annees INTEGER GENERATED ALWAYS AS (
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_embauche))
    ) STORED,
    secteur_geographique VARCHAR(200),
    statut VARCHAR(20),
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension Entrepôt
CREATE TABLE dw.dim_entrepot (
    id_entrepot SERIAL PRIMARY KEY,
    id_entrepot_source INTEGER NOT NULL, -- Référence à la table OLTP
    nom VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    ville VARCHAR(50),
    superficie DECIMAL(10,2),
    capacite_stockage DECIMAL(10,2),
    statut VARCHAR(20) DEFAULT 'actif',
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension Transporteur
CREATE TABLE dw.dim_transporteur (
    id_transporteur SERIAL PRIMARY KEY,
    id_transporteur_source INTEGER NOT NULL, -- Référence à la table OLTP
    raison_sociale VARCHAR(200) NOT NULL,
    contact VARCHAR(100),
    telephone VARCHAR(20),
    tarif_km DECIMAL(8,3),
    zones_couvertes TEXT,
    statut VARCHAR(20) DEFAULT 'actif',
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- FAITS
-- =============================================

-- Table des faits Ventes
CREATE TABLE dw.fait_ventes (
    id_vente SERIAL PRIMARY KEY,
    id_temps INTEGER NOT NULL REFERENCES dw.dim_temps(id_temps),
    id_client INTEGER NOT NULL REFERENCES dw.dim_client(id_client),
    id_produit INTEGER NOT NULL REFERENCES dw.dim_produit(id_produit),
    id_commercial INTEGER NOT NULL REFERENCES dw.dim_commercial(id_commercial),
    id_commande_source INTEGER NOT NULL,
    id_ligne_commande_source INTEGER NOT NULL,
    
    -- Mesures
    quantite_vendue INTEGER NOT NULL,
    prix_unitaire_ht DECIMAL(10,2) NOT NULL,
    remise_pct DECIMAL(5,2) DEFAULT 0.00,
    montant_ht DECIMAL(12,2) NOT NULL,
    montant_tva DECIMAL(12,2) GENERATED ALWAYS AS (montant_ht * 0.20) STORED,
    montant_ttc DECIMAL(12,2) GENERATED ALWAYS AS (montant_ht * 1.20) STORED,
    
    -- Coûts et marges
    cout_achat_ht DECIMAL(12,2) NOT NULL,
    marge_brute_ht DECIMAL(12,2) GENERATED ALWAYS AS (montant_ht - cout_achat_ht) STORED,
    marge_brute_pct DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN montant_ht > 0 THEN ((montant_ht - cout_achat_ht) / montant_ht) * 100
            ELSE 0 
        END
    ) STORED,
    
    -- Indicateurs de performance
    est_commande_complete BOOLEAN DEFAULT TRUE,
    est_retour BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des faits Stocks
CREATE TABLE dw.fait_stocks (
    id_mouvement_stock SERIAL PRIMARY KEY,
    id_temps INTEGER NOT NULL REFERENCES dw.dim_temps(id_temps),
    id_produit INTEGER NOT NULL REFERENCES dw.dim_produit(id_produit),
    id_entrepot INTEGER NOT NULL REFERENCES dw.dim_entrepot(id_entrepot),
    id_mouvement_source INTEGER NOT NULL,
    
    -- Mesures
    quantite_avant_mouvement INTEGER NOT NULL,
    quantite_mouvement INTEGER NOT NULL,
    quantite_apres_mouvement INTEGER NOT NULL,
    type_mouvement VARCHAR(20) NOT NULL,
    
    -- Coûts associés
    valeur_stock_ht DECIMAL(12,2) GENERATED ALWAYS AS (quantite_apres_mouvement * 
        (SELECT prix_achat_ht FROM dw.dim_produit WHERE id_produit = dw.dim_produit.id_produit LIMIT 1)
    ) STORED,
    
    -- Indicateurs de performance
    est_mouvement_anormal BOOLEAN DEFAULT FALSE,
    est_alerte_stock BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des faits Livraisons
CREATE TABLE dw.fait_livraisons (
    id_livraison SERIAL PRIMARY KEY,
    id_temps INTEGER NOT NULL REFERENCES dw.dim_temps(id_temps),
    id_client INTEGER NOT NULL REFERENCES dw.dim_client(id_client),
    id_transporteur INTEGER NOT NULL REFERENCES dw.dim_transporteur(id_transporteur),
    id_commande_source INTEGER NOT NULL,
    id_livraison_source INTEGER NOT NULL,
    
    -- Mesures
    nombre_colis INTEGER DEFAULT 1,
    poids_total DECIMAL(10,3) DEFAULT 0,
    volume_total DECIMAL(10,3) DEFAULT 0,
    cout_transport_ht DECIMAL(12,2) NOT NULL,
    
    -- Performance livraison
    delai_livraison_jours INTEGER,
    est_livraison_ponctuelle BOOLEAN DEFAULT TRUE,
    est_retour BOOLEAN DEFAULT FALSE,
    motif_retour TEXT,
    
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des faits Facturation
CREATE TABLE dw.fait_facturation (
    id_facture SERIAL PRIMARY KEY,
    id_temps INTEGER NOT NULL REFERENCES dw.dim_temps(id_temps),
    id_client INTEGER NOT NULL REFERENCES dw.dim_client(id_client),
    id_commande_source INTEGER NOT NULL,
    id_facture_source INTEGER NOT NULL,
    
    -- Mesures financières
    montant_facture_ht DECIMAL(12,2) NOT NULL,
    montant_tva DECIMAL(12,2) NOT NULL,
    montant_ttc DECIMAL(12,2) NOT NULL,
    
    -- Gestion des paiements
    delai_paiement_jours INTEGER,
    est_en_retard_paiement BOOLEAN DEFAULT FALSE,
    montant_retard DECIMAL(12,2) DEFAULT 0,
    
    -- Indicateurs
    date_echeance DATE,
    date_paiement_effective DATE,
    mode_paiement VARCHAR(50),
    
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEX POUR PERFORMANCE
-- =============================================

-- Index sur les dimensions
CREATE INDEX idx_dim_temps_date ON dw.dim_temps(date_complete);
CREATE INDEX idx_dim_temps_annee_mois ON dw.dim_temps(annee, mois);
CREATE INDEX idx_dim_client_raison_sociale ON dw.dim_client(raison_sociale);
CREATE INDEX idx_dim_client_secteur ON dw.dim_client(secteur_activite);
CREATE INDEX idx_dim_client_segment ON dw.dim_client(segment_client);
CREATE INDEX idx_dim_produit_reference ON dw.dim_produit(reference);
CREATE INDEX idx_dim_produit_famille ON dw.dim_produit(famille_produit);
CREATE INDEX idx_dim_produit_categorie_marge ON dw.dim_produit(categorie_marge);
CREATE INDEX idx_dim_commercial_nom ON dw.dim_commercial(nom_complet);
CREATE INDEX idx_dim_entrepot_nom ON dw.dim_entrepot(nom);
CREATE INDEX idx_dim_transporteur_raison_sociale ON dw.dim_transporteur(raison_sociale);

-- Index sur les tables de faits
CREATE INDEX idx_fait_ventes_temps ON dw.fait_ventes(id_temps);
CREATE INDEX idx_fait_ventes_client ON dw.fait_ventes(id_client);
CREATE INDEX idx_fait_ventes_produit ON dw.fait_ventes(id_produit);
CREATE INDEX idx_fait_ventes_commercial ON dw.fait_ventes(id_commercial);
CREATE INDEX idx_fait_ventes_commande ON dw.fait_ventes(id_commande_source);

CREATE INDEX idx_fait_stocks_temps ON dw.fait_stocks(id_temps);
CREATE INDEX idx_fait_stocks_produit ON dw.fait_stocks(id_produit);
CREATE INDEX idx_fait_stocks_entrepot ON dw.fait_stocks(id_entrepot);
CREATE INDEX idx_fait_stocks_type ON dw.fait_stocks(type_mouvement);

CREATE INDEX idx_fait_livraisons_temps ON dw.fait_livraisons(id_temps);
CREATE INDEX idx_fait_livraisons_client ON dw.fait_livraisons(id_client);
CREATE INDEX idx_fait_livraisons_transporteur ON dw.fait_livraisons(id_transporteur);
CREATE INDEX idx_fait_livraisons_ponctuelle ON dw.fait_livraisons(est_livraison_ponctuelle);

CREATE INDEX idx_fait_facturation_temps ON dw.fait_facturation(id_temps);
CREATE INDEX idx_fait_facturation_client ON dw.fait_facturation(id_client);
CREATE INDEX idx_fait_facturation_retard ON dw.fait_facturation(est_en_retard_paiement);

-- =============================================
-- VUES AGGÉGÉES POUR PERFORMANCE
-- =============================================

-- Vue agrégée ventes mensuelles par client
CREATE MATERIALIZED VIEW dw.v_ventes_mensuelles_client AS
SELECT 
    d.id_client,
    d.raison_sociale,
    d.secteur_activite,
    d.segment_client,
    t.annee,
    t.mois,
    t.periode_mois,
    SUM(f.quantite_vendue) as quantite_totale,
    SUM(f.montant_ht) as ca_ht,
    SUM(f.cout_achat_ht) as cout_achat_total,
    SUM(f.marge_brute_ht) as marge_brute_totale,
    AVG(f.marge_brute_pct) as marge_moyenne_pct,
    COUNT(DISTINCT f.id_commande_source) as nombre_commandes
FROM dw.fait_ventes f
JOIN dw.dim_temps t ON f.id_temps = t.id_temps
JOIN dw.dim_client d ON f.id_client = d.id_client
GROUP BY d.id_client, d.raison_sociale, d.secteur_activite, d.segment_client, t.annee, t.mois, t.periode_mois;

-- Vue agrégée ventes mensuelles par produit
CREATE MATERIALIZED VIEW dw.v_ventes_mensuelles_produit AS
SELECT 
    p.id_produit,
    p.reference,
    p.libelle,
    p.famille_produit,
    p.categorie_marge,
    t.annee,
    t.mois,
    t.periode_mois,
    SUM(f.quantite_vendue) as quantite_totale,
    SUM(f.montant_ht) as ca_ht,
    SUM(f.cout_achat_ht) as cout_achat_total,
    SUM(f.marge_brute_ht) as marge_brute_totale,
    AVG(f.marge_brute_pct) as marge_moyenne_pct,
    COUNT(DISTINCT f.id_commande_source) as nombre_commandes
FROM dw.fait_ventes f
JOIN dw.dim_temps t ON f.id_temps = t.id_tempos
JOIN dw.dim_produit p ON f.id_produit = p.id_produit
GROUP BY p.id_produit, p.reference, p.libelle, p.famille_produit, p.categorie_marge, t.annee, t.mois, t.periode_mois;

-- Vue agrégée performance commerciale
CREATE MATERIALIZED VIEW dw.v_performance_commerciale AS
SELECT 
    c.id_commercial,
    c.nom_complet,
    c.secteur_geographique,
    t.annee,
    t.mois,
    t.periode_mois,
    SUM(f.montant_ht) as ca_ht,
    SUM(f.marge_brute_ht) as marge_brute_totale,
    COUNT(DISTINCT f.id_client) as nombre_clients_actifs,
    COUNT(DISTINCT f.id_commande_source) as nombre_commandes,
    AVG(f.montant_ht) as panier_moyen_ht,
    AVG(f.marge_brute_pct) as marge_moyenne_pct
FROM dw.fait_ventes f
JOIN dw.dim_temps t ON f.id_temps = t.id_temps
JOIN dw.dim_commercial c ON f.id_commercial = c.id_commercial
GROUP BY c.id_commercial, c.nom_complet, c.secteur_geographique, t.annee, t.mois, t.periode_mois;

-- Vue agrégée état des stocks
CREATE MATERIALIZED VIEW dw.v_etat_stocks_actuel AS
SELECT 
    p.id_produit,
    p.reference,
    p.libelle,
    p.famille_produit,
    e.nom as entrepot_nom,
    e.region,
    SUM(s.quantite_apres_mouvement) as stock_actuel,
    p.seuil_alerte_stock,
    CASE 
        WHEN SUM(s.quantite_apres_mouvement) <= p.seuil_alerte_stock THEN 'ALERTE'
        WHEN SUM(s.quantite_apres_mouvement) >= p.seuil_alerte_stock * 5 THEN 'SURSTOCK'
        ELSE 'NORMAL'
    END as statut_stock,
    SUM(s.valeur_stock_ht) as valeur_stock_ht
FROM dw.fait_stocks s
JOIN dw.dim_produit p ON s.id_produit = p.id_produit
JOIN dw.dim_entrepot e ON s.id_entrepot = e.id_entrepot
WHERE s.id_temps = (SELECT MAX(id_temps) FROM dw.fait_stocks)
GROUP BY p.id_produit, p.reference, p.libelle, p.famille_produit, e.nom, e.region, p.seuil_alerte_stock;

-- =============================================
-- COMMENTAIRES POUR DOCUMENTATION
-- =============================================

COMMENT ON SCHEMA dw IS 'Data Warehouse EcoDistribution - Schéma en étoile';
COMMENT ON TABLE dw.dim_temps IS 'Dimension temporelle avec toutes les hiérarchies de dates';
COMMENT ON TABLE dw.dim_client IS 'Dimension client avec informations démographiques et segmentations';
COMMENT ON TABLE dw.dim_produit IS 'Dimension produit avec caractéristiques et classifications';
COMMENT ON TABLE dw.dim_commercial IS 'Dimension commercial avec informations sur l''équipe de vente';
COMMENT ON TABLE dw.dim_entrepot IS 'Dimension entrepôt avec informations logistiques';
COMMENT ON TABLE dw.dim_transporteur IS 'Dimension transporteur avec informations sur les partenaires logistiques';
COMMENT ON TABLE dw.fait_ventes IS 'Table des faits ventes - cœur de l''analytique commercial';
COMMENT ON TABLE dw.fait_stocks IS 'Table des faits mouvements de stocks pour l''analytique logistique';
COMMENT ON TABLE dw.fait_livraisons IS 'Table des faits livraisons pour la performance logistique';
COMMENT ON TABLE dw.fait_facturation IS 'Table des faits facturation pour le suivi financier';
