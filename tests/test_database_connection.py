"""
Tests unitaires pour les connexions base de données
EcoDistribution - Plateforme décisionnelle
"""

import pytest
from unittest.mock import Mock, patch
import sqlalchemy

from etl.src.database_connection import DatabaseConnection


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
        
    def test_initialize_failure(self):
        """Test l'initialisation échouée"""
        conn_string = "postgresql://user:pass@localhost/db"
        db_conn = DatabaseConnection(conn_string)
        
        with patch('etl.src.database_connection.create_engine') as mock_create_engine:
            mock_create_engine.side_effect = sqlalchemy.exc.SQLAlchemyError("Erreur de connexion")
            
            with pytest.raises(sqlalchemy.exc.SQLAlchemyError):
                db_conn.initialize()
                
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
        
    def test_get_session_success(self):
        """Test la création de session réussie"""
        db_conn = DatabaseConnection("postgresql://user:pass@localhost/db")
        mock_engine = Mock()
        mock_session = Mock()
        mock_session_factory = Mock(return_value=mock_session)
        
        db_conn.engine = mock_engine
        db_conn.session_factory = mock_session_factory
        
        with db_conn.get_session() as session:
            assert session == mock_session
            
        mock_session_factory.assert_called_once()
        
    def test_get_session_without_engine(self):
        """Test la création de session sans moteur initialisé"""
        db_conn = DatabaseConnection("postgresql://user:pass@localhost/db")
        
        with pytest.raises(Exception, match="Le moteur de base de données n'est pas initialisé"):
            with db_conn.get_session():
                pass


if __name__ == "__main__":
    pytest.main([__file__])
