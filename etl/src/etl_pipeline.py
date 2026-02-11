"""
Pipeline ETL principal pour EcoDistribution
Extraction, Transformation et Loading des données de l'OLTP vers le Data Warehouse
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd

from .database_connection import oltp_conn, dw_conn

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETLPipeline:
    """Pipeline ETL principal pour l'alimentation du Data Warehouse"""
    
    def __init__(self) -> None:
        """Initialise le pipeline ETL"""
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.stats: Dict[str, any] = {
            'dimensions_loaded': 0,
            'facts_loaded': 0,
            'errors': []
        }
    
    def run_full_etl(self) -> bool:
        """Exécute le pipeline ETL complet"""
        self.start_time = datetime.now()
        logger.info("Début du pipeline ETL complet")
        
        try:
            # 1. Charger les dimensions
            if not self._load_dimensions():
                raise Exception("Échec du chargement des dimensions")
            
            # 2. Charger les tables de faits
            if not self._load_facts():
                raise Exception("Échec du chargement des faits")
            
            # 3. Rafraîchir les vues matérialisées
            if not self._refresh_materialized_views():
                raise Exception("Échec du rafraîchissement des vues")
            
            self.end_time = datetime.now()
            duration = self.end_time - self.start_time
            logger.info(f"Pipeline ETL terminé avec succès en {duration}")
            return True
            
        except Exception as e:
            self.end_time = datetime.now()
            error_msg = f"Erreur lors de l'exécution du pipeline ETL: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
            self.stats['errors'].append(str(e))
            return False
    
    def _load_dimensions(self):
        """Charge toutes les tables de dimensions"""
        logger.info("Chargement des dimensions...")
        
        dimensions = [
            'dim_temps',
            'dim_client', 
            'dim_produit',
            'dim_commercial',
            'dim_entrepot',
            'dim_transporteur'
        ]
        
        for dim_name in dimensions:
            try:
                if dim_name == 'dim_temps':
                    self._load_dim_temps()
                else:
                    self._load_dimension(dim_name)
                self.stats['dimensions_loaded'] += 1
                logger.info(f"Dimension {dim_name} chargée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {dim_name}: {e}")
                self.stats['errors'].append(f"Erreur {dim_name}: {str(e)}")
    
    def _load_dim_temps(self):
        """Charge la dimension temps (génération automatique)"""
        logger.info("Génération de la dimension temps...")
        
        # Générer les dates pour les 3 dernières années + 1 an futur
        start_date = datetime.now() - timedelta(days=3*365)
        end_date = datetime.now() + timedelta(days=365)
        
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            dates.append({
                'date_complete': current_date.date(),
                'annee': current_date.year,
                'trimestre': (current_date.month - 1) // 3 + 1,
                'mois': current_date.month,
                'jour': current_date.day,
                'jour_semaine': current_date.weekday() + 1,
                'nom_jour': current_date.strftime('%A'),
                'nom_mois': current_date.strftime('%B'),
                'nom_trimestre': f"T{((current_date.month - 1) // 3 + 1)}-{current_date.year}",
                'semaine_annee': current_date.isocalendar()[1],
                'est_jour_ferie': False,  # À implémenter avec un calendrier des jours fériés
                'est_weekend': current_date.weekday() >= 5,
                'periode_mois': current_date.strftime('%Y-%m'),
                'periode_trimestre': f"{current_date.year}-Q{((current_date.month - 1) // 3 + 1)}",
                'periode_annee': str(current_date.year)
            })
            current_date += timedelta(days=1)
        
        # Insérer dans le Data Warehouse
        df_temps = pd.DataFrame(dates)
        
        with dw_conn.get_session() as session:
            # Supprimer les données existantes
            session.execute("DELETE FROM dw.dim_temps")
            
            # Insérer les nouvelles données
            for _, row in df_temps.iterrows():
                insert_sql = """
                INSERT INTO dw.dim_temps (
                    date_complete, annee, trimestre, mois, jour, jour_semaine,
                    nom_jour, nom_mois, nom_trimestre, semaine_annee,
                    est_jour_ferie, est_weekend, periode_mois, periode_trimestre, periode_annee
                ) VALUES (
                    :date_complete, :annee, :trimestre, :mois, :jour, :jour_semaine,
                    :nom_jour, :nom_mois, :nom_trimestre, :semaine_annee,
                    :est_jour_ferie, :est_weekend, :periode_mois, :periode_trimestre, :periode_annee
                )
                """
                session.execute(insert_sql, row.to_dict())
    
    def _load_dimension(self, dim_name: str):
        """Charge une dimension spécifique depuis l'OLTP vers le DW"""
        
        # Mapping des dimensions avec leurs requêtes de chargement
        dimension_queries = {
            'dim_client': """
                INSERT INTO dw.dim_client (
                    id_client_source, raison_sociale, siret, secteur_activite,
                    taille_entreprise, region, departement, code_postal, ville,
                    condition_paiement, remise_contractuelle, date_creation, statut
                )
                SELECT 
                    c.id_client, c.raison_sociale, c.siret, c.secteur_activite,
                    c.taille_entreprise, 
                    CASE 
                        WHEN c.code_postal LIKE '01%' THEN 'Auvergne-Rhône-Alpes'
                        WHEN c.code_postal LIKE '02%' THEN 'Hauts-de-France'
                        WHEN c.code_postal LIKE '03%' THEN 'Auvergne-Rhône-Alpes'
                        WHEN c.code_postal LIKE '04%' THEN 'Provence-Alpes-Côte d''Azur'
                        WHEN c.code_postal LIKE '05%' THEN 'Provence-Alpes-Côte d''Azur'
                        WHEN c.code_postal LIKE '06%' THEN 'Provence-Alpes-Côte d''Azur'
                        WHEN c.code_postal LIKE '69%' THEN 'Auvergne-Rhône-Alpes'
                        WHEN c.code_postal LIKE '13%' THEN 'Provence-Alpes-Côte d''Azur'
                        WHEN c.code_postal LIKE '59%' THEN 'Hauts-de-France'
                        ELSE 'Autre'
                    END as region,
                    SUBSTRING(c.code_postal, 1, 2) as departement,
                    c.code_postal, c.ville, c.condition_paiement, c.remise_contractuelle,
                    c.date_creation, c.statut
                FROM T_CLIENTS c
                ON CONFLICT (id_client_source) DO UPDATE SET
                    raison_sociale = EXCLUDED.raison_sociale,
                    siret = EXCLUDED.siret,
            """,
            'dim_produit': """
                SELECT 
                    p.id_produit,
                    p.reference_produit,
                    p.libelle_produit,
                    p.description,
                    p.prix_unitaire_ht,
                    p.unite_mesure,
                    p.poids_net,
                    p.volume,
                    f.libelle_famille,
                    p.date_creation,
                    p.statut
                FROM t_produits p
                JOIN t_familles_produits f ON p.id_famille = f.id_famille
                WHERE p.statut = 'ACTIF'
            """,
            'dim_entrepot': """
                SELECT 
                    e.id_entrepot,
                    e.nom,
                    e.adresse,
                    e.code_postal,
                    e.ville,
                    e.superficie,
                    e.capacite_stockage,
                    e.date_creation
                FROM t_entrepots e
            """,
            'dim_commercial': """
                SELECT 
                    co.id_commercial,
                    co.nom,
                    co.prenom,
                    co.email,
                    co.telephone,
                    co.date_embauche,
                    co.statut,
                    co.commission_taux
                FROM t_commerciaux co
                WHERE co.statut = 'ACTIF'
            """
        }
        
        return queries.get(table_name, "")
    
    def _transform_dimension_data(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Transforme les données d'une dimension"""
        try:
            # Nettoyage de base
            df = df.drop_duplicates()
            df = df.dropna()
            
            # Transformations spécifiques par table
            if table_name == 'dim_temps':
                df['date_complete'] = pd.to_datetime(df['date_complete'])
                df = df.sort_values('date_complete')
                
            elif table_name == 'dim_client':
                df['raison_sociale'] = df['raison_sociale'].str.strip().str.upper()
                df['siret'] = df['siret'].astype(str).str.replace(' ', '')
                
            elif table_name == 'dim_produit':
                df['reference_produit'] = df['reference_produit'].str.strip().str.upper()
                df['libelle_produit'] = df['libelle_produit'].str.strip()
                
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors de la transformation des données {table_name}: {e}")
            raise
    
    def _load_facts(self) -> bool:
        """Charge les tables de faits"""
        logger.info("Chargement des faits...")
        
        try:
            facts = ['fait_ventes', 'fait_stocks', 'fait_livraisons']
            
            for fact_table in facts:
                if not self._load_fact_table(fact_table):
                    error_msg = f"Échec du chargement des faits {fact_table}"
                    logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
                    return False
                    
            logger.info("Tous les faits chargés avec succès")
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors du chargement des faits: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def _load_fact_table(self, table_name: str) -> bool:
        """Charge une table de faits spécifique"""
        try:
            logger.info(f"Chargement des faits {table_name}...")
            
            # Extraction depuis OLTP
            query = self._get_fact_query(table_name)
            df = oltp_conn.execute_query(query)
            
            if df.empty:
                logger.warning(f"Aucune donnée trouvée pour {table_name}")
                return True
            
            # Transformation si nécessaire
            df_transformed = self._transform_fact_data(df, table_name)
            
            # Chargement dans DW avec déduplication
            rows_inserted = dw_conn.upsert_data(df_transformed, table_name)
            
            self.stats['facts_loaded'] += rows_inserted
            logger.info(f"Fait {table_name}: {rows_inserted} lignes insérées/mises à jour")
            
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors du chargement de {table_name}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def _get_fact_query(self, table_name: str) -> str:
        """Retourne la requête SQL pour extraire une table de faits"""
        queries = {
            'fait_ventes': """
                INSERT INTO dw.fait_ventes (
                    id_temps, id_client, id_produit, id_commercial,
                    id_commande_source, id_ligne_commande_source,
                    quantite_vendue, prix_unitaire_ht, remise_pct,
                    montant_ht, cout_achat_ht
                )
                SELECT 
                    dt.id_temps, dc.id_client, dp.id_produit, dco.id_commercial,
                    c.id_commande, lc.id_ligne,
                    lc.quantite_commandee, lc.prix_unitaire_ht, lc.remise_ligne,
                    lc.montant_ligne_ht, lc.quantite_commandee * p.prix_achat_ht
                FROM T_COMMANDES_CLIENTS c
                JOIN T_LIGNES_COMMANDE lc ON c.id_commande = lc.id_commande
                JOIN T_PRODUITS p ON lc.id_produit = p.id_produit
                JOIN dw.dim_temps dt ON dt.date_complete = c.date_commande
                JOIN dw.dim_client dc ON dc.id_client_source = c.id_client
                JOIN dw.dim_produit dp ON dp.id_produit_source = lc.id_produit
                LEFT JOIN dw.dim_commercial dco ON dco.id_commercial_source = c.id_commercial
                WHERE c.statut NOT IN ('annulee')
            """,
            
            'fait_stocks': """
                INSERT INTO dw.fait_stocks (
                    id_temps, id_produit, id_entrepot, id_mouvement_source,
                    quantite_avant_mouvement, quantite_mouvement, quantite_apres_mouvement,
                    type_mouvement
                )
                SELECT 
                    dt.id_temps, dp.id_produit, de.id_entrepot, ms.id_mouvement,
                    s.quantite_disponible - ms.quantite as quantite_avant,
                    ms.quantite, s.quantite_disponible as quantite_apres,
                    ms.type_mouvement
                FROM T_MOUVEMENTS_STOCKS ms
                JOIN T_STOCKS s ON ms.id_stock = s.id_stock
                JOIN T_PRODUITS p ON s.id_produit = p.id_produit
                JOIN T_ENTREPOTS e ON s.id_entrepot = e.id_entrepot
                JOIN dw.dim_temps dt ON dt.date_complete = DATE(ms.date_mouvement)
                JOIN dw.dim_produit dp ON dp.id_produit_source = s.id_produit
                JOIN dw.dim_entrepot de ON de.id_entrepot_source = s.id_entrepot
            """,
            
            'fait_livraisons': """
                INSERT INTO dw.fait_livraisons (
                    id_temps, id_client, id_transporteur, id_commande_source,
                    id_livraison_source, cout_transport_ht, delai_livraison_jours,
                    est_livraison_ponctuelle
                )
                SELECT 
                    COALESCE(dt_livraison.id_temps, dt_expedition.id_tempos) as id_temps,
                    dc.id_client, dtr.id_transporteur, l.id_commande, l.id_livraison,
                    l.cout_transport,
                    CASE 
                        WHEN l.date_livraison_effective IS NOT NULL AND c.date_livraison_prevue IS NOT NULL
                        THEN l.date_livraison_effective - c.date_livraison_prevue
                        ELSE NULL
                    END as delai_livraison_jours,
                    CASE 
                        WHEN l.date_livraison_effective <= c.date_livraison_prevue OR l.date_livraison_effective IS NULL
                        THEN TRUE
                        ELSE FALSE
                    END as est_livraison_ponctuelle
                FROM T_LIVRAISONS l
                JOIN T_COMMANDES_CLIENTS c ON l.id_commande = c.id_commande
                JOIN dw.dim_client dc ON dc.id_client_source = c.id_client
                LEFT JOIN dw.dim_transporteur dtr ON dtr.id_transporteur_source = l.id_transporteur
                LEFT JOIN dw.dim_temps dt_expedition ON dt_expedition.date_complete = l.date_expedition
                LEFT JOIN dw.dim_temps dt_livraison ON dt_livraison.date_complete = l.date_livraison_effective
                WHERE l.statut NOT IN ('annulee')
            """,
            
            'fait_facturation': """
                INSERT INTO dw.fait_facturation (
                    id_temps, id_client, id_commande_source, id_facture_source,
                    montant_facture_ht, montant_tva, montant_ttc,
                    delai_paiement_jours, est_en_retard_paiement
                )
                SELECT 
                    dt.id_temps, dc.id_client, f.id_commande, f.id_facture,
                    f.montant_ht, f.montant_tva, f.montant_ttc,
                    CASE 
                        WHEN f.date_paiement IS NOT NULL AND f.date_facture IS NOT NULL
                        THEN f.date_paiement - f.date_facture
                        WHEN f.date_echeance IS NOT NULL AND f.date_facture IS NOT NULL
                        THEN f.date_echeance - f.date_facture
                        ELSE NULL
                    END as delai_paiement_jours,
                    CASE 
                        WHEN f.statut = 'en_retard' THEN TRUE
                        ELSE FALSE
                    END as est_en_retard_paiement
                FROM T_FACTURES f
                JOIN T_COMMANDES_CLIENTS c ON f.id_commande = c.id_commande
                JOIN dw.dim_client dc ON dc.id_client_source = c.id_client
                JOIN dw.dim_temps dt ON dt.date_complete = f.date_facture
                WHERE f.statut NOT IN ('annulee')
            """
        }
        
        if fact_name not in fact_queries:
            raise ValueError(f"Table de faits {fact_name} non reconnue")
        
        with dw_conn.get_session() as session:
            session.execute(fact_queries[fact_name])
    
    def _refresh_materialized_views(self):
        """Rafraîchit les vues matérialisées pour la performance"""
        logger.info("Rafraîchissement des vues matérialisées...")
        
        views = [
            'dw.v_ventes_mensuelles_client',
            'dw.v_ventes_mensuelles_produit', 
            'dw.v_performance_commerciale',
            'dw.v_etat_stocks_actuel'
        ]
        
        for view in views:
            try:
                with dw_conn.get_session() as session:
                    session.execute(f"REFRESH MATERIALIZED VIEW {view}")
                logger.info(f"Vue {view} rafraîchie")
            except Exception as e:
                logger.error(f"Erreur lors du rafraîchissement de {view}: {e}")
                self.stats['errors'].append(f"Erreur vue {view}: {str(e)}")
    
    def get_execution_stats(self) -> Dict:
        """Retourne les statistiques d'exécution du pipeline"""
        stats = self.stats.copy()
        if self.start_time and self.end_time:
            stats['duration'] = str(self.end_time - self.start_time)
        stats['success'] = len(stats['errors']) == 0
        return stats

if __name__ == "__main__":
    # Test du pipeline ETL
    from .database_connection import initialize_connections
    
    if initialize_connections():
        pipeline = ETLPipeline()
        success = pipeline.run_full_etl()
        stats = pipeline.get_execution_stats()
        
        print(f"Pipeline ETL {'réussi' if success else 'échoué'}")
        print(f"Durée: {stats.get('duration', 'N/A')}")
        print(f"Dimensions chargées: {stats['dimensions_loaded']}")
        print(f"Faits chargés: {stats['facts_loaded']}")
        if stats['errors']:
            print(f"Erreurs: {stats['errors']}")
    else:
        print("Impossible d'initialiser les connexions aux bases de données")
