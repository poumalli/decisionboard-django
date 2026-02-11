"""
Tests unitaires pour le pipeline ETL
EcoDistribution - Plateforme décisionnelle
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime

from etl.src.etl_pipeline import ETLPipeline
from etl.src.database_connection import DatabaseConnection


class TestETLPipeline:
    """Tests pour la classe ETLPipeline"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.pipeline = ETLPipeline()
        
    @patch('etl.src.etl_pipeline.oltp_conn')
    @patch('etl.src.etl_pipeline.dw_conn')
    def test_init_pipeline(self, mock_dw, mock_oltp):
        """Test l'initialisation du pipeline"""
        pipeline = ETLPipeline()
        
        assert pipeline.start_time is None
        assert pipeline.end_time is None
        assert pipeline.stats['dimensions_loaded'] == 0
        assert pipeline.stats['facts_loaded'] == 0
        assert pipeline.stats['errors'] == []
        
    def test_get_execution_stats_empty(self):
        """Test la récupération des stats quand pipeline n'a pas tourné"""
        stats = self.pipeline.get_execution_stats()
        
        assert stats['success'] is False
        assert stats['duration'] is None
        assert stats['dimensions_loaded'] == 0
        assert stats['facts_loaded'] == 0
        assert stats['errors'] == []
        
    @patch('etl.src.etl_pipeline.oltp_conn')
    def test_load_dimensions_success(self, mock_oltp):
        """Test le chargement des dimensions avec succès"""
        # Mock des données de test
        mock_data = pd.DataFrame({
            'id_client': [1, 2],
            'raison_sociale': ['Client A', 'Client B'],
            'siret': ['123456789', '987654321']
        })
        
        mock_oltp.execute_query.return_value = mock_data
        
        # Mock de la connexion DW
        with patch('etl.src.etl_pipeline.dw_conn') as mock_dw:
            mock_dw.insert_data.return_value = True
            
            result = self.pipeline._load_dimensions()
            
            assert result is True
            assert self.pipeline.stats['dimensions_loaded'] > 0
            assert len(self.pipeline.stats['errors']) == 0
            
    @patch('etl.src.etl_pipeline.oltp_conn')
    def test_load_dimensions_with_error(self, mock_oltp):
        """Test le chargement des dimensions avec erreur"""
        mock_oltp.execute_query.side_effect = Exception("Erreur de connexion")
        
        result = self.pipeline._load_dimensions()
        
        assert result is False
        assert len(self.pipeline.stats['errors']) > 0
        assert "Erreur de connexion" in str(self.pipeline.stats['errors'][0])
        
    @patch('etl.src.etl_pipeline.oltp_conn')
    @patch('etl.src.etl_pipeline.dw_conn')
    def test_load_facts_success(self, mock_dw, mock_oltp):
        """Test le chargement des faits avec succès"""
        # Mock des données de test
        mock_data = pd.DataFrame({
            'id_commande': [1, 2],
            'id_client': [1, 2],
            'montant_ht': [100.0, 200.0],
            'date_commande': ['2024-01-01', '2024-01-02']
        })
        
        mock_oltp.execute_query.return_value = mock_data
        mock_dw.insert_data.return_value = True
        
        result = self.pipeline._load_facts()
        
        assert result is True
        assert self.pipeline.stats['facts_loaded'] > 0
        assert len(self.pipeline.stats['errors']) == 0
        
    def test_run_full_etl_success(self):
        """Test l'exécution complète du pipeline avec succès"""
        with patch.object(self.pipeline, '_load_dimensions', return_value=True), \
             patch.object(self.pipeline, '_load_facts', return_value=True), \
             patch.object(self.pipeline, '_refresh_materialized_views', return_value=True):
            
            result = self.pipeline.run_full_etl()
            
            assert result is True
            assert self.pipeline.start_time is not None
            assert self.pipeline.end_time is not None
            assert self.pipeline.stats['dimensions_loaded'] > 0
            assert self.pipeline.stats['facts_loaded'] > 0
            
    def test_run_full_etl_with_error(self):
        """Test l'exécution complète du pipeline avec erreur"""
        with patch.object(self.pipeline, '_load_dimensions', return_value=False):
            
            result = self.pipeline.run_full_etl()
            
            assert result is False
            assert len(self.pipeline.stats['errors']) > 0


class TestDatabaseConnection:
    """Tests pour la classe DatabaseConnection"""
    
    def test_init_connection(self):
        """Test l'initialisation de la connexion"""
        conn_string = "postgresql://user:pass@localhost/db"
        db_conn = DatabaseConnection(conn_string)
        
        assert db_conn.connection_string == conn_string
        assert db_conn.engine is None
        assert db_conn.session_factory is None
        
    @patch('etl.src.database_connection.create_engine')
    @patch('etl.src.database_connection.sessionmaker')
    def test_initialize_success(self, mock_session_factory, mock_create_engine):
        """Test l'initialisation réussie"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        conn_string = "postgresql://user:pass@localhost/db"
        db_conn = DatabaseConnection(conn_string)
        
        db_conn.initialize()
        
        assert db_conn.engine == mock_engine
        mock_create_engine.assert_called_once()
        mock_session_factory.assert_called_once_with(bind=mock_engine)
        
    def test_test_connection_success(self):
        """Test le test de connexion réussi"""
        db_conn = DatabaseConnection("postgresql://user:pass@localhost/db")
        mock_engine = Mock()
        mock_connection = Mock()
        mock_result = Mock()
        mock_result.scalar.return_value = 1
        
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.__exit__.return_value = None
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value = mock_connection
        
        db_conn.engine = mock_engine
        
        result = db_conn.test_connection()
        
        assert result is True
        mock_connection.execute.assert_called_once()
        
    def test_test_connection_failure(self):
        """Test le test de connexion échoué"""
        db_conn = DatabaseConnection("postgresql://user:pass@localhost/db")
        mock_engine = Mock()
        mock_engine.connect.side_effect = Exception("Erreur de connexion")
        
        db_conn.engine = mock_engine
        
        result = db_conn.test_connection()
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
