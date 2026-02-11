"""
Configuration des bases de données pour la chaîne ETL
EcoDistribution - Plateforme décisionnelle
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """Configuration de connexion à une base de données"""
    host: str
    port: int
    database: str
    username: str
    password: str
    schema: Optional[str] = None
    
    def get_connection_string(self) -> str:
        """Génère la chaîne de connexion PostgreSQL"""
        if self.schema:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?options=-csearch_path%3D{self.schema}"
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class DatabaseManager:
    """Gestionnaire des configurations de base de données"""
    
    def __init__(self):
        self.oltp_config = self._get_oltp_config()
        self.dw_config = self._get_dw_config()
    
    def _get_oltp_config(self) -> DatabaseConfig:
        """Configuration pour la base de données OLTP"""
        return DatabaseConfig(
            host=os.getenv('OLTP_HOST', 'localhost'),
            port=int(os.getenv('OLTP_PORT', '5432')),
            database=os.getenv('OLTP_DATABASE', 'ecodistribution_oltp'),
            username=os.getenv('OLTP_USERNAME', 'postgres'),
            password=os.getenv('OLTP_PASSWORD', 'password'),
            schema='public'
        )
    
    def _get_dw_config(self) -> DatabaseConfig:
        """Configuration pour le Data Warehouse"""
        return DatabaseConfig(
            host=os.getenv('DW_HOST', 'localhost'),
            port=int(os.getenv('DW_PORT', '5432')),
            database=os.getenv('DW_DATABASE', 'ecodistribution_dw'),
            username=os.getenv('DW_USERNAME', 'postgres'),
            password=os.getenv('DW_PASSWORD', 'password'),
            schema='dw'
        )
    
    def get_oltp_connection(self) -> str:
        """Retourne la chaîne de connexion OLTP"""
        return self.oltp_config.get_connection_string()
    
    def get_dw_connection(self) -> str:
        """Retourne la chaîne de connexion DW"""
        return self.dw_config.get_connection_string()

# Instance globale du gestionnaire de configuration
db_manager = DatabaseManager()

# Configurations pour l'environnement de développement
if __name__ == "__main__":
    print("Configuration OLTP:", db_manager.get_oltp_connection())
    print("Configuration DW:", db_manager.get_dw_connection())
