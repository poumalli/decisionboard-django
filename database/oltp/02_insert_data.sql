-- Données de test pour EcoDistribution
-- Insertion des données de référence

-- =============================================
-- FAMILLES DE PRODUITS
-- =============================================

INSERT INTO T_FAMILLES_PRODUITS (libelle_famille, description) VALUES
('Produits d''entretien', 'Produits de nettoyage écologiques pour surfaces et sols'),
('Emballages biodégradables', 'Emballages et contenants compostables'),
('Équipements durables', 'Matériel réutilisable et éco-responsable'),
('Produits d''hygiène', 'Produits sanitaires et d''hygiène personnelle écologiques'),
('Consommables verts', 'Papier recyclé, stylos rechargeables, etc.');

-- =============================================
-- ENTREPÔTS
-- =============================================

INSERT INTO T_ENTREPOTS (nom, adresse, code_postal, ville, superficie, capacite_stockage) VALUES
('Entrepôt Lyon', '123 Rue de l''Industrie, ZI Nord', '69000', 'Lyon', 1500.00, 3000.00),
('Entrepôt Marseille', '456 Avenue du Port, Zone Maritime', '13000', 'Marseille', 1200.00, 2500.00),
('Entrepôt Lille', '789 Boulevard de la Logistique', '59000', 'Lille', 1000.00, 2000.00);

-- =============================================
-- TRANSPORTEURS
-- =============================================

INSERT INTO T_TRANSPORTEURS (raison_sociale, contact, telephone, email, tarif_km, zones_couvertes) VALUES
('EcoTransport SA', 'Jean Martin', '04 72 12 34 56', 'contact@ecotransport.fr', 0.85, 'Rhône-Alpes, Auvergne'),
('GreenLogistics', 'Marie Dubois', '04 91 23 45 67', 'info@greenlogistics.fr', 0.92, 'PACA, Languedoc-Roussillon'),
('EcoDelivery Nord', 'Pierre Lefebvre', '03 20 98 76 54', 'service@ecodelivery-nord.fr', 0.78, 'Nord-Pas-de-Calais, Picardie');

-- =============================================
-- COMMERCIAUX
-- =============================================

INSERT INTO T_COMMERCIAUX (nom, prenom, email, telephone, date_embauche, secteur_geographique) VALUES
('Durand', 'Sophie', 's.durand@ecodistribution.fr', '06 12 34 56 78', '2022-01-15', 'Région Rhône-Alpes'),
('Bernard', 'Thomas', 't.bernard@ecodistribution.fr', '06 23 45 67 89', '2021-06-10', 'Région PACA'),
('Petit', 'Claire', 'c.petit@ecodistribution.fr', '06 34 56 78 90', '2022-09-01', 'Région Nord');

-- =============================================
-- FOURNISSEURS
-- =============================================

INSERT INTO T_FOURNISSEURS (raison_sociale, siret, adresse, code_postal, ville, telephone, email, delai_livraison_standard) VALUES
('BioClean Products', '12345678901234', '15 Rue Écologique', '69000', 'Lyon', '04 72 11 22 33', 'contact@bioclean.fr', 5),
('EcoPack Solutions', '23456789012345', '22 Avenue Durable', '13000', 'Marseille', '04 91 44 55 66', 'info@ecopack.fr', 7),
('GreenTech Industries', '34567890123456', '33 Boulevard Vert', '59000', 'Lille', '03 20 77 88 99', 'commercial@greentech.fr', 10);

-- =============================================
-- CLIENTS
-- =============================================

INSERT INTO T_CLIENTS (raison_sociale, siret, secteur_activite, taille_entreprise, adresse, code_postal, ville, telephone, email, remise_contractuelle, id_commercial_affected) VALUES
('Hôtel Les Oliviers', '45678901234567', 'Hôtellerie', 'PME', '12 Avenue des Pins', '06000', 'Nice', '04 93 12 34 56', 'contact@hotel-oliviers.fr', 5.00, 2),
('Restaurant Le Gourmet', '56789012345678', 'Restauration', 'TPE', '8 Rue de la Table', '69000', 'Lyon', '04 78 23 45 67', 'reservations@legourmet.fr', 3.00, 1),
('Bureau Conseil Alpha', '67890123456789', 'Services', 'PME', '45 Rue de la République', '69000', 'Lyon', '04 72 34 56 78', 'contact@bureau-alpha.fr', 8.00, 1),
('Supermarché BioStore', '78901234567890', 'Grande distribution', 'ETI', '200 Route du Commerce', '13000', 'Marseille', '04 91 45 67 89', 'achats@biostore.fr', 12.00, 2),
('École Primaire Verte', '89012345678901', 'Éducation', 'TPE', '3 Rue des Écoliers', '59000', 'Lille', '03 20 56 78 90', 'secretariat@ecole-verte.fr', 10.00, 3);

-- =============================================
-- PRODUITS
-- =============================================

INSERT INTO T_PRODUITS (reference, libelle, id_famille_produit, description, poids, volume, prix_achat_ht, prix_vente_ht, seuil_alerte_stock, delai_livraison_fournisseur, id_fournisseur_principal) VALUES
-- Produits d'entretien
('PE001', 'Nettoyant Multi-Usage Écologique 1L', 1, 'Nettoyant concentré biodégradable pour toutes surfaces', 1.050, 0.001, 2.50, 4.20, 20, 5, 1),
('PE002', 'Lessive Liquide Éco 5L', 1, 'Lessive concentrée hypoallergénique', 5.200, 0.005, 8.00, 13.50, 15, 5, 1),
('PE003', 'Dégraissant Cuisine Écologique 750ml', 1, 'Dégraissant puissant et biodégradable', 0.800, 0.001, 3.20, 5.80, 25, 5, 1),
('PE004', 'Produit Vaisselle Éco 1L', 1, 'Liquide vaisselle naturel et efficace', 1.100, 0.001, 2.80, 4.90, 30, 5, 1),

-- Emballages biodégradables
('EB001', 'Sachet Compostable 30x40cm', 2, 'Sachet biodégradable pour aliments', 0.050, 0.0001, 0.15, 0.35, 100, 7, 2),
('EB002', 'Boîte Lunch Biodégradable', 2, 'Contenant repas compostable', 0.200, 0.001, 0.80, 1.50, 50, 7, 2),
('EB003', 'Film Étirable Compostable 30m', 2, 'Film alimentaire biodégradable', 0.300, 0.0005, 2.20, 3.90, 40, 7, 2),
('EB004', 'Gobelet Carton Compostable 25cl', 2, 'Gobelet pour boissons chaudes/froides', 0.080, 0.0002, 0.25, 0.55, 80, 7, 2),

-- Équipements durables
('ED001', 'Gourde Inox 500ml', 3, 'Gourde réutilisable en acier inoxydable', 0.250, 0.0005, 5.50, 9.90, 30, 10, 3),
('ED002', 'Sac Tissu Réutilisable', 3, 'Sac de courses en coton biologique', 0.150, 0.0003, 2.80, 5.20, 40, 10, 3),
('ED003', 'Paille Réutilisable Inox', 3, 'Set de 4 pailles en inox avec brosse', 0.100, 0.0001, 3.20, 6.50, 25, 10, 3),
('ED004', 'Boîte Conservation Verre 1L', 3, 'Boîte en verre avec couvercle bambou', 0.600, 0.001, 4.50, 8.20, 20, 10, 3),

-- Produits d'hygiène
('PH001', 'Savon Liquide Écologique 300ml', 4, 'Savon mains naturel et doux', 0.350, 0.0004, 1.80, 3.20, 60, 5, 1),
('PH002', 'Gel Hydroalcoolique Éco 500ml', 4, 'Gel désinfectant biodegradable', 0.550, 0.0005, 2.90, 5.10, 45, 5, 1),
('PH003', 'Papier Toilette Recyclé 12 rouleaux', 4, 'Papier toilette 100% recyclé', 2.000, 0.003, 4.20, 7.80, 35, 7, 2),
('PH004', 'Serviettes en Tissu Réutilisables', 4, 'Set de 6 serviettes en coton bio', 0.400, 0.001, 6.80, 12.50, 15, 10, 3),

-- Consommables verts
('CG001', 'Stylos Rechargeables (x10)', 5, 'Stylos bille avec recharges', 0.200, 0.0005, 8.50, 14.90, 25, 10, 3),
('CG002', 'Carnet Notes Papier Recyclé A5', 5, 'Carnet 100 pages papier recyclé', 0.300, 0.0004, 2.20, 4.10, 50, 7, 2),
('CG003', 'Classeur Carton Recyclé', 5, 'Classeur 4cm en carton recyclé', 0.500, 0.002, 3.80, 6.90, 30, 7, 2),
('CG004', 'Surligneur Alcool-Free (x4)', 5, 'Surligneurs à l''eau sans alcool', 0.150, 0.0003, 3.50, 6.20, 40, 10, 3);

-- =============================================
-- STOCKS INITIAUX
-- =============================================

INSERT INTO T_STOCKS (id_produit, id_entrepot, quantite_disponible, seuil_min, seuil_max) VALUES
-- Entrepôt Lyon
(1, 1, 150, 20, 200), (2, 1, 80, 15, 150), (3, 1, 200, 25, 250), (4, 1, 120, 30, 180),
(5, 1, 500, 100, 800), (6, 1, 60, 50, 120), (7, 1, 80, 40, 150), (8, 1, 200, 80, 300),
(9, 1, 40, 30, 80), (10, 1, 60, 40, 100), (11, 1, 30, 25, 60), (12, 1, 25, 20, 50),
(13, 1, 80, 60, 120), (14, 1, 100, 45, 150), (15, 1, 60, 35, 100), (16, 1, 40, 15, 60),
(17, 1, 150, 50, 200), (18, 1, 80, 40, 120), (19, 1, 40, 30, 80), (20, 1, 60, 25, 100),

-- Entrepôt Marseille
(1, 2, 100, 20, 150), (2, 2, 60, 15, 100), (3, 2, 150, 25, 200), (4, 2, 80, 30, 120),
(5, 2, 300, 100, 500), (6, 2, 40, 50, 80), (7, 2, 60, 40, 100), (8, 2, 150, 80, 200),
(9, 2, 30, 30, 60), (10, 2, 40, 40, 80), (11, 2, 20, 25, 40), (12, 2, 15, 20, 30),
(13, 2, 50, 60, 80), (14, 2, 70, 45, 100), (15, 2, 40, 35, 70), (16, 2, 25, 15, 40),
(17, 2, 100, 50, 150), (18, 2, 50, 40, 80), (19, 2, 25, 30, 50), (20, 2, 40, 25, 70),

-- Entrepôt Lille
(1, 3, 80, 20, 120), (2, 3, 50, 15, 80), (3, 3, 120, 25, 150), (4, 3, 60, 30, 100),
(5, 3, 250, 100, 400), (6, 3, 35, 50, 70), (7, 3, 50, 40, 80), (8, 3, 120, 80, 180),
(9, 3, 25, 30, 50), (10, 3, 35, 40, 70), (11, 3, 18, 25, 35), (12, 3, 12, 20, 25),
(13, 3, 40, 60, 70), (14, 3, 55, 45, 80), (15, 3, 35, 35, 60), (16, 3, 20, 15, 35),
(17, 3, 80, 50, 120), (18, 3, 40, 40, 70), (19, 3, 20, 30, 40), (20, 3, 35, 25, 60);

-- =============================================
-- COMMANDES CLIENTS (EXEMPLES)
-- =============================================

INSERT INTO T_COMMANDES_CLIENTS (numero_commande, id_client, date_commande, date_livraison_prevue, statut, id_commercial) VALUES
('CMD-2024-001', 1, '2024-01-15', '2024-01-20', 'livree', 2),
('CMD-2024-002', 2, '2024-01-18', '2024-01-23', 'livree', 1),
('CMD-2024-003', 3, '2024-01-22', '2024-01-27', 'expediee', 1),
('CMD-2024-004', 4, '2024-01-25', '2024-01-30', 'confirmee', 2),
('CMD-2024-005', 5, '2024-01-28', '2024-02-02', 'en_attente', 3),
('CMD-2024-006', 1, '2024-02-01', '2024-02-06', 'confirmee', 2),
('CMD-2024-007', 2, '2024-02-03', '2024-02-08', 'en_attente', 1),
('CMD-2024-008', 4, '2024-02-05', '2024-02-10', 'confirmee', 2);

-- =============================================
-- LIGNES DE COMMANDE
-- =============================================

INSERT INTO T_LIGNES_COMMANDE (id_commande, id_produit, quantite_commandee, prix_unitaire_ht, remise_ligne) VALUES
-- Commande CMD-2024-001 (Hôtel Les Oliviers)
(1, 1, 20, 4.20, 5.00), (1, 2, 10, 13.50, 5.00), (1, 13, 15, 3.20, 5.00), (1, 14, 25, 5.10, 5.00),

-- Commande CMD-2024-002 (Restaurant Le Gourmet)
(2, 1, 5, 4.20, 3.00), (2, 3, 8, 5.80, 3.00), (2, 4, 12, 4.90, 3.00), (2, 6, 30, 1.50, 3.00),

-- Commande CMD-2024-003 (Bureau Conseil Alpha)
(3, 17, 20, 3.20, 8.00), (3, 18, 15, 5.10, 8.00), (3, 19, 10, 7.80, 8.00), (3, 21, 8, 14.90, 8.00),

-- Commande CMD-2024-004 (Supermarché BioStore)
(4, 5, 200, 0.35, 12.00), (4, 6, 100, 1.50, 12.00), (4, 7, 150, 3.90, 12.00), (4, 8, 300, 0.55, 12.00),

-- Commande CMD-2024-005 (École Primaire Verte)
(5, 17, 10, 3.20, 10.00), (5, 18, 8, 5.10, 10.00), (5, 19, 5, 7.80, 10.00), (5, 21, 3, 14.90, 10.00),

-- Commande CMD-2024-006 (Hôtel Les Oliviers - nouvelle commande)
(6, 1, 15, 4.20, 5.00), (6, 2, 8, 13.50, 5.00), (6, 9, 10, 9.90, 5.00), (6, 10, 12, 5.20, 5.00),

-- Commande CMD-2024-007 (Restaurant Le Gourmet - nouvelle commande)
(7, 1, 3, 4.20, 3.00), (7, 3, 5, 5.80, 3.00), (7, 4, 8, 4.90, 3.00), (7, 6, 20, 1.50, 3.00),

-- Commande CMD-2024-008 (Supermarché BioStore - nouvelle commande)
(8, 5, 150, 0.35, 12.00), (8, 6, 80, 1.50, 12.00), (8, 7, 120, 3.90, 12.00), (8, 8, 250, 0.55, 12.00);

-- =============================================
-- FACTURES
-- =============================================

INSERT INTO T_FACTURES (numero_facture, id_commande, date_facture, date_echeance, statut) VALUES
('FAC-2024-001', 1, '2024-01-15', '2024-02-28', 'payee'),
('FAC-2024-002', 2, '2024-01-18', '2024-03-01', 'payee'),
('FAC-2024-003', 3, '2024-01-22', '2024-03-05', 'payee'),
('FAC-2024-004', 4, '2024-01-25', '2024-03-08', 'emise'),
('FAC-2024-005', 5, '2024-01-28', '2024-03-11', 'emise'),
('FAC-2024-006', 6, '2024-02-01', '2024-03-14', 'emise'),
('FAC-2024-007', 7, '2024-02-03', '2024-03-16', 'emise'),
('FAC-2024-008', 8, '2024-02-05', '2024-03-18', 'emise');

-- =============================================
-- LIVRAISONS
-- =============================================

INSERT INTO T_LIVRAISONS (id_commande, id_transporteur, date_expedition, date_livraison_effective, cout_transport, statut, numero_suivi) VALUES
(1, 1, '2024-01-18', '2024-01-20', 15.50, 'livree', 'ETR123456789FR'),
(2, 1, '2024-01-21', '2024-01-23', 12.00, 'livree', 'ETR987654321FR'),
(3, 1, '2024-01-25', '2024-01-27', 18.00, 'expediee', 'ETR456789123FR'),
(4, 2, '2024-01-28', NULL, 45.00, 'expediee', 'GRN789456123FR'),
(5, 3, NULL, NULL, NULL, 'preparee', NULL),
(6, 1, '2024-02-04', NULL, 14.50, 'expediee', 'ETR321654987FR'),
(7, 1, NULL, NULL, NULL, 'preparee', NULL),
(8, 2, '2024-02-08', NULL, 42.00, 'expediee', 'GRN159753456FR');
