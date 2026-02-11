"""
Gestion des connexions aux bases de données
EcoDistribution - Plateforme décisionnelle
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..config.database_config import db_manager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Classe de gestion des connexions aux bases de données"""
    
    def __init__(self, connection_string: str) -> None:
        """Initialise la connexion base de données
        
        Args:
            connection_string: Chaîne de connexion PostgreSQL
        """
        self.connection_string: str = connection_string
        self.engine: Optional[sqlalchemy.Engine] = None
        self.session_factory: Optional[sessionmaker] = None
    
    def initialize(self) -> None:
        """Initialise le moteur de base de données et la factory de sessions"""
        try:
            self.engine = create_engine(
                self.connection_string,
                poolclass=StaticPool,
                pool_pre_ping=True,
                echo=False  # Mettre à True pour le debug SQL
            )
            self.session_factory = sessionmaker(bind=self.engine)
            logger.info("Connexion à la base de données initialisée avec succès")
        except Exception as e:
            error_msg = f"Erreur lors de l'initialisation de la connexion: {e}"
            logger.error(error_msg)
            raise
    
    def test_connection(self) -> bool:
        """Teste la connexion à la base de données
        
        Returns:
            True si la connexion fonctionne, False sinon
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            error_msg = f"Erreur lors du test de connexion: {e}"
            logger.error(error_msg)
            return False
    
    @contextmanager
    def get_session(self) -> Generator[sqlalchemy.orm.Session, None, None]:
        """Context manager pour obtenir une session de base de données
        
        Yields:
            Session SQLAlchemy active
        """
        if self.engine is None or self.session_factory is None:
            raise Exception("Le moteur de base de données n'est pas initialisé")
            
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la session: {e}"
            logger.error(error_msg)
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str) -> 'pd.DataFrame':
        """Exécute une requête SQL et retourne les résultats
        
        Args:
            query: Requête SQL à exécuter
            
        Returns:
            DataFrame pandas avec les résultats
        """
        try:
            import pandas as pd
            
            with self.engine.connect() as connection:
                df = pd.read_sql(query, connection)
                logger.info(f"Requête exécutée: {len(df)} lignes retournées")
                return df
                
        except Exception as e:
            error_msg = f"Erreur lors de l'exécution de la requête: {e}"
            logger.error(error_msg)
            raise
    
    def insert_data(self, df: 'pd.DataFrame', table_name: str) -> int:
        """Insère des données dans une table
        
        Args:
            df: DataFrame à insérer
            table_name: Nom de la table cible
            
        Returns:
            Nombre de lignes insérées
        """
        try:
            with self.engine.connect() as connection:
                rows_inserted = df.to_sql(
                    table_name, 
                    connection, 
                    if_exists='append', 
                    index=False,
                    method='multi'
                )
                logger.info(f"Insertion dans {table_name}: {rows_inserted} lignes")
                return rows_inserted
                
        except Exception as e:
            error_msg = f"Erreur lors de l'insertion dans {table_name}: {e}"
            logger.error(error_msg)
            raise
    
    def upsert_data(self, df: 'pd.DataFrame', table_name: str) -> int:
        """Insère ou met à jour des données (idempotent)
        
        Args:
            df: DataFrame à insérer/mettre à jour
            table_name: Nom de la table cible
            
        Returns:
            Nombre de lignes traitées
        """
        try:
            # Pour l'instant, implémentation simple avec suppression+insertion
            # TODO: Implémenter vrai UPSERT avec ON CONFLICT
            
            # Identification de la clé primaire selon la table
            primary_keys = {
                'dim_temps': 'date_complete',
                'dim_client': 'id_client_source',
                'dim_produit': 'id_produit_source',
                'dim_entrepot': 'id_entrepot_source',
                'dim_commercial': 'id_commercial_source',
                'fait_ventes': 'id_ligne_commande_source',
                'fait_stocks': 'id_mouvement_source',
                'fait_livraisons': 'id_livraison_source'
            }
            
            pk_column = primary_keys.get(table_name)
            if not pk_column:
                raise Exception(f"Clé primaire non définie pour la table {table_name}")
            
            with self.engine.connect() as connection:
                # Suppression des lignes existantes
                if pk_column in df.columns:
                    existing_ids = df[pk_column].tolist()
                    if existing_ids:
                        delete_query = f"DELETE FROM {table_name} WHERE {pk_column} IN ({','.join(['%s'] * len(existing_ids))})"
                        connection.execute(text(delete_query), existing_ids)
                
                # Insertion des nouvelles données
                rows_inserted = df.to_sql(
                    table_name,
                    connection,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                
                logger.info(f"UPSERT dans {table_name}: {rows_inserted} lignes traitées")
                return rows_inserted
                
        except Exception as e:
            error_msg = f"Erreur lors de l'UPSERT dans {table_name}: {e}"
            logger.error(error_msg)
            raise
            return False
    
    @contextmanager
    def get_session(self) -> Generator[sqlalchemy.orm.Session, None, None]:
        """Context manager pour les sessions de base de données"""
        if not self.session_factory:
            raise RuntimeError("La connexion n'a pas été initialisée")
        
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur lors de la transaction: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[dict] = None) -> list:
        """Exécute une requête SQL et retourne les résultats"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {e}")
            raise
    
    def execute_script(self, script_path: str) -> None:
        """Exécute un script SQL depuis un fichier"""
        try:
            with open(script_path, 'r', encoding='utf-8') as file:
                script_content = file.read()
            
            with self.engine.connect() as connection:
                connection.execute(text(script_content))
                connection.commit()
            logger.info(f"Script {script_path} exécuté avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du script {script_path}: {e}")
            raise

class OLTPConnection(DatabaseConnection):
    """Connexion spécialisée pour la base OLTP"""
    
    def __init__(self):
        super().__init__(db_manager.get_oltp_connection())

class DWConnection(DatabaseConnection):
    """Connexion spécialisée pour le Data Warehouse"""
    
    def __init__(self):
        super().__init__(db_manager.get_dw_connection())

# Instances globales des connexions
oltp_conn = OLTPConnection()
dw_conn = DWConnection()

def initialize_connections():
    """Initialise toutes les connexions aux bases de données"""
    try:
        oltp_conn.initialize()
        dw_conn.initialize()
        
        # Test des connexions
        if not oltp_conn.test_connection():
            raise RuntimeError("Impossible de se connecter à la base OLTP")
        
        if not dw_conn.test_connection():
            raise RuntimeError("Impossible de se connecter au Data Warehouse")
        
        logger.info("Toutes les connexions initialisées avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des connexions: {e}")
        return False

if __name__ == "__main__":
    # Test des connexions
    if initialize_connections():
        print("Connexions établies avec succès")
        
        # Test de requête simple
        try:
            result = oltp_conn.execute_query("SELECT COUNT(*) as count FROM T_CLIENTS")
            print(f"Nombre de clients: {result[0]['count']}")
        except Exception as e:
            print(f"Erreur lors du test: {e}")
    else:
        print("Échec de l'initialisation des connexions")
