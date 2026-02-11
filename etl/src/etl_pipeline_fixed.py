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
    
    def _load_dimensions(self) -> bool:
        """Charge toutes les tables de dimensions"""
        logger.info("Chargement des dimensions...")
        
        try:
            dimensions = [
                'dim_temps',
                'dim_client', 
                'dim_produit',
                'dim_entrepot',
                'dim_commercial'
            ]
            
            for dim_table in dimensions:
                if not self._load_dimension_table(dim_table):
                    error_msg = f"Échec du chargement de la dimension {dim_table}"
                    logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
                    return False
                    
            logger.info("Toutes les dimensions chargées avec succès")
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors du chargement des dimensions: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def _load_dimension_table(self, table_name: str) -> bool:
        """Charge une table de dimension spécifique"""
        try:
            logger.info(f"Chargement de la dimension {table_name}...")
            
            # Extraction depuis OLTP
            query = self._get_dimension_query(table_name)
            if not query:
                logger.warning(f"Requête non trouvée pour {table_name}")
                return True
                
            df = oltp_conn.execute_query(query)
            
            if df.empty:
                logger.warning(f"Aucune donnée trouvée pour {table_name}")
                return True
            
            # Transformation si nécessaire
            df_transformed = self._transform_dimension_data(df, table_name)
            
            # Chargement dans DW avec déduplication
            rows_inserted = dw_conn.upsert_data(df_transformed, table_name)
            
            self.stats['dimensions_loaded'] += rows_inserted
            logger.info(f"Dimension {table_name}: {rows_inserted} lignes insérées/mises à jour")
            
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors du chargement de {table_name}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def _get_dimension_query(self, table_name: str) -> str:
        """Retourne la requête SQL pour extraire une dimension"""
        queries = {
            'dim_temps': """
                SELECT DISTINCT 
                    date_commande as date_complete,
                    EXTRACT(YEAR FROM date_commande) as annee,
                    EXTRACT(QUARTER FROM date_commande) as trimestre,
                    EXTRACT(MONTH FROM date_commande) as mois,
                    EXTRACT(DAY FROM date_commande) as jour,
                    EXTRACT(DOW FROM date_commande) as jour_semaine,
                    TO_CHAR(date_commande, 'Day') as nom_jour,
                    TO_CHAR(date_commande, 'Month') as nom_mois,
                    'Q' || EXTRACT(QUARTER FROM date_commande) as nom_trimestre,
                    EXTRACT(WEEK FROM date_commande) as semaine_annee,
                    FALSE as est_jour_ferie,
                    (EXTRACT(DOW FROM date_commande) IN (0, 6)) as est_weekend,
                    TO_CHAR(date_commande, 'YYYY-MM') as periode_mois,
                    TO_CHAR(date_commande, 'YYYY-"Q"Q') as periode_trimestre,
                    TO_CHAR(date_commande, 'YYYY') as periode_annee
                FROM t_commandes
                WHERE date_commande IS NOT NULL
            """,
            'dim_client': """
                SELECT 
                    c.id_client,
                    c.raison_sociale,
                    c.siret,
                    c.secteur_activite,
                    c.taille_entreprise,
                    CASE 
                        WHEN c.code_postal LIKE '69%' OR c.code_postal LIKE '38%' THEN 'Auvergne-Rhône-Alpes'
                        WHEN c.code_postal LIKE '04%' OR c.code_postal LIKE '05%' OR c.code_postal LIKE '06%' OR c.code_postal LIKE '13%' OR c.code_postal LIKE '83%' OR c.code_postal LIKE '84%' THEN 'Provence-Alpes-Côte d\'Azur'
                        WHEN c.code_postal LIKE '59%' THEN 'Hauts-de-France'
                        ELSE 'Autre'
                    END as region,
                    SUBSTRING(c.code_postal, 1, 2) as departement,
                    c.code_postal, c.ville, c.condition_paiement, c.remise_contractuelle,
                    c.date_creation, c.statut
                FROM t_clients c
                WHERE c.statut = 'ACTIF'
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
                if 'date_complete' in df.columns:
                    df['date_complete'] = pd.to_datetime(df['date_complete'])
                    df = df.sort_values('date_complete')
                
            elif table_name == 'dim_client':
                if 'raison_sociale' in df.columns:
                    df['raison_sociale'] = df['raison_sociale'].str.strip().str.upper()
                if 'siret' in df.columns:
                    df['siret'] = df['siret'].astype(str).str.replace(' ', '')
                
            elif table_name == 'dim_produit':
                if 'reference_produit' in df.columns:
                    df['reference_produit'] = df['reference_produit'].str.strip().str.upper()
                if 'libelle_produit' in df.columns:
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
            if not query:
                logger.warning(f"Requête non trouvée pour {table_name}")
                return True
                
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
                SELECT 
                    c.id_commande,
                    lc.id_ligne,
                    lc.id_produit,
                    lc.id_client,
                    lc.id_commercial,
                    lc.quantite,
                    lc.prix_unitaire_ht,
                    lc.remise_pct,
                    lc.montant_ht,
                    c.date_commande
                FROM t_lignes_commandes lc
                JOIN t_commandes c ON lc.id_commande = c.id_commande
                WHERE c.statut = 'VALIDEE'
            """,
            'fait_stocks': """
                SELECT 
                    ms.id_mouvement_stock,
                    ms.id_produit,
                    ms.id_entrepot,
                    ms.type_mouvement,
                    ms.quantite,
                    ms.date_mouvement,
                    ms.motif
                FROM t_mouvements_stocks ms
                WHERE ms.date_mouvement >= CURRENT_DATE - INTERVAL '30 days'
            """,
            'fait_livraisons': """
                SELECT 
                    l.id_livraison,
                    l.id_commande,
                    l.id_transporteur,
                    l.date_livraison,
                    l.statut_livraison,
                    l.cout_livraison_ht
                FROM t_livraisons l
                WHERE l.date_livraison >= CURRENT_DATE - INTERVAL '30 days'
            """
        }
        
        return queries.get(table_name, "")
    
    def _transform_fact_data(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Transforme les données d'une table de faits"""
        try:
            # Nettoyage de base
            df = df.drop_duplicates()
            df = df.dropna()
            
            # Transformations spécifiques par table
            if table_name == 'fait_ventes':
                if 'date_commande' in df.columns:
                    df['date_commande'] = pd.to_datetime(df['date_commande'])
                if 'montant_ht' in df.columns:
                    df['montant_ht'] = pd.to_numeric(df['montant_ht'], errors='coerce')
                
            elif table_name == 'fait_stocks':
                if 'date_mouvement' in df.columns:
                    df['date_mouvement'] = pd.to_datetime(df['date_mouvement'])
                if 'quantite' in df.columns:
                    df['quantite'] = pd.to_numeric(df['quantite'], errors='coerce')
                
            elif table_name == 'fait_livraisons':
                if 'date_livraison' in df.columns:
                    df['date_livraison'] = pd.to_datetime(df['date_livraison'])
                if 'cout_livraison_ht' in df.columns:
                    df['cout_livraison_ht'] = pd.to_numeric(df['cout_livraison_ht'], errors='coerce')
                
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors de la transformation des faits {table_name}: {e}")
            raise
    
    def _refresh_materialized_views(self) -> bool:
        """Rafraîchit les vues matérialisées du Data Warehouse"""
        logger.info("Rafraîchissement des vues matérialisées...")
        
        try:
            views = [
                'mv_kpi_mensuels',
                'mv_top_clients',
                'mv_top_produits',
                'mv_performance_commerciaux'
            ]
            
            for view in views:
                try:
                    dw_conn.execute_query(f"REFRESH MATERIALIZED VIEW {view}")
                    logger.info(f"Vue {view} rafraîchie")
                except Exception as e:
                    logger.warning(f"Impossible de rafraîchir la vue {view}: {e}")
            
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors du rafraîchissement des vues: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def get_execution_stats(self) -> Dict[str, any]:
        """Retourne les statistiques d'exécution du pipeline"""
        duration = None
        if self.start_time and self.end_time:
            duration = str(self.end_time - self.start_time)
            
        return {
            'success': len(self.stats['errors']) == 0 and self.start_time is not None,
            'duration': duration,
            'dimensions_loaded': self.stats['dimensions_loaded'],
            'facts_loaded': self.stats['facts_loaded'],
            'errors': self.stats['errors']
        }
