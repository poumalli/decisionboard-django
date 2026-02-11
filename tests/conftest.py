"""
Configuration pytest pour les tests
EcoDistribution - Plateforme décisionnelle
"""

import pytest
import os
import sys
from unittest.mock import Mock

# Ajout du répertoire src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'etl', 'src'))

@pytest.fixture
def mock_oltp_data():
    """Fixture pour les données OLTP de test"""
    return {
        'clients': [
            {'id_client': 1, 'raison_sociale': 'Client Test A', 'siret': '123456789'},
            {'id_client': 2, 'raison_sociale': 'Client Test B', 'siret': '987654321'}
        ],
        'commandes': [
            {'id_commande': 1, 'id_client': 1, 'montant_ht': 100.0, 'date_commande': '2024-01-01'},
            {'id_commande': 2, 'id_client': 2, 'montant_ht': 200.0, 'date_commande': '2024-01-02'}
        ]
    }

@pytest.fixture
def mock_database_connection():
    """Fixture pour mock les connexions base de données"""
    mock_conn = Mock()
    mock_conn.execute_query.return_value = []
    mock_conn.insert_data.return_value = True
    return mock_conn

@pytest.fixture
def sample_etl_stats():
    """Fixture pour les statistiques ETL de test"""
    return {
        'success': True,
        'duration': '00:05:30',
        'dimensions_loaded': 5,
        'facts_loaded': 100,
        'errors': []
    }
