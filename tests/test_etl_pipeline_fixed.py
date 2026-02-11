"""
Tests unitaires pour le pipeline ETL corrigé
EcoDistribution - Plateforme décisionnelle
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime

from etl.src.etl_pipeline_fixed import ETLPipeline


class TestETLPipelineFixed:
    """Tests pour la classe ETLPipeline corrigée"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.pipeline = ETLPipeline()
        
    def test_init_pipeline(self):
        """Test l'initialisation du pipeline"""
        assert self.pipeline.start_time is None
        assert self.pipeline.end_time is None
        assert self.pipeline.stats['dimensions_loaded'] == 0
        assert self.pipeline.stats['facts_loaded'] == 0
        assert self.pipeline.stats['errors'] == []
        
    def test_get_execution_stats_empty(self):
        """Test la récupération des stats quand pipeline n'a pas tourné"""
        stats = self.pipeline.get_execution_stats()
        
        assert stats['success'] is False
        assert stats['duration'] is None
        assert stats['dimensions_loaded'] == 0
        assert stats['facts_loaded'] == 0
        assert stats['errors'] == []
        
    @patch('etl.src.etl_pipeline_fixed.oltp_conn')
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
        with patch('etl.src.etl_pipeline_fixed.dw_conn') as mock_dw:
            mock_dw.upsert_data.return_value = 2
            
            result = self.pipeline._load_dimensions()
            
            assert result is True
            assert self.pipeline.stats['dimensions_loaded'] > 0
            assert len(self.pipeline.stats['errors']) == 0
            
    @patch('etl.src.etl_pipeline_fixed.oltp_conn')
    def test_load_dimensions_with_error(self, mock_oltp):
        """Test le chargement des dimensions avec erreur"""
        mock_oltp.execute_query.side_effect = Exception("Erreur de connexion")
        
        result = self.pipeline._load_dimensions()
        
        assert result is False
        assert len(self.pipeline.stats['errors']) > 0
        assert "Erreur de connexion" in str(self.pipeline.stats['errors'][0])
        
    @patch('etl.src.etl_pipeline_fixed.oltp_conn')
    @patch('etl.src.etl_pipeline_fixed.dw_conn')
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
        mock_dw.upsert_data.return_value = 2
        
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
            
    def test_run_full_etl_with_error(self):
        """Test l'exécution complète du pipeline avec erreur"""
        with patch.object(self.pipeline, '_load_dimensions', return_value=False):
            
            result = self.pipeline.run_full_etl()
            
            assert result is False
            assert len(self.pipeline.stats['errors']) > 0
            
    def test_get_dimension_query(self):
        """Test la récupération des requêtes de dimensions"""
        query = self.pipeline._get_dimension_query('dim_client')
        
        assert 'SELECT' in query
        assert 't_clients' in query
        assert 'WHERE c.statut = \'ACTIF\'' in query
        
        # Test avec une table inexistante
        query_empty = self.pipeline._get_dimension_query('table_inexistante')
        assert query_empty == ""
        
    def test_get_fact_query(self):
        """Test la récupération des requêtes de faits"""
        query = self.pipeline._get_fact_query('fait_ventes')
        
        assert 'SELECT' in query
        assert 't_lignes_commandes' in query
        assert 'WHERE c.statut = \'VALIDEE\'' in query
        
        # Test avec une table inexistante
        query_empty = self.pipeline._get_fact_query('table_inexistante')
        assert query_empty == ""
        
    def test_transform_dimension_data(self):
        """Test la transformation des données de dimensions"""
        df = pd.DataFrame({
            'raison_sociale': ['  client test  ', 'CLIENT B'],
            'siret': ['123 456 789', '987654321']
        })
        
        result = self.pipeline._transform_dimension_data(df, 'dim_client')
        
        assert result['raison_sociale'].iloc[0] == 'CLIENT TEST'
        assert result['siret'].iloc[0] == '123456789'
        
    def test_transform_fact_data(self):
        """Test la transformation des données de faits"""
        df = pd.DataFrame({
            'montant_ht': ['100.5', '200.3'],
            'date_commande': ['2024-01-01', '2024-01-02']
        })
        
        result = self.pipeline._transform_fact_data(df, 'fait_ventes')
        
        assert pd.api.types.is_datetime64_any_dtype(result['date_commande'])
        assert pd.api.types.is_numeric_dtype(result['montant_ht'])


if __name__ == "__main__":
    pytest.main([__file__])
