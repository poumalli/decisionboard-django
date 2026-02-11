"""
Point d'entrée principal pour la chaîne ETL
EcoDistribution - Plateforme décisionnelle
"""

import argparse
import logging
import sys
from datetime import datetime

from database_connection import initialize_connections
from etl_pipeline import ETLPipeline

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Fonction principale du programme ETL"""
    
    parser = argparse.ArgumentParser(description='Pipeline ETL EcoDistribution')
    parser.add_argument(
        '--mode', 
        choices=['full', 'dimensions', 'facts', 'test'],
        default='full',
        help='Mode d\'exécution du pipeline'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Active le mode verbeux'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 50)
    logger.info("Démarrage du pipeline ETL EcoDistribution")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Heure de début: {datetime.now()}")
    logger.info("=" * 50)
    
    try:
        # Initialisation des connexions
        logger.info("Initialisation des connexions aux bases de données...")
        if not initialize_connections():
            logger.error("Impossible d'initialiser les connexions")
            return 1
        
        # Création et exécution du pipeline
        pipeline = ETLPipeline()
        
        if args.mode == 'test':
            logger.info("Mode test: Vérification des connexions uniquement")
            return 0
        
        elif args.mode == 'full':
            success = pipeline.run_full_etl()
            
        elif args.mode == 'dimensions':
            pipeline._load_dimensions()
            success = True
            
        elif args.mode == 'facts':
            pipeline._load_facts()
            success = True
        
        # Affichage des statistiques
        stats = pipeline.get_execution_stats()
        
        logger.info("=" * 50)
        logger.info("Statistiques d'exécution:")
        logger.info(f"Succès: {stats['success']}")
        logger.info(f"Durée: {stats.get('duration', 'N/A')}")
        logger.info(f"Dimensions chargées: {stats['dimensions_loaded']}")
        logger.info(f"Faits chargés: {stats['facts_loaded']}")
        
        if stats['errors']:
            logger.error("Erreurs rencontrées:")
            for error in stats['errors']:
                logger.error(f"  - {error}")
        
        logger.info("=" * 50)
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Erreur critique lors de l'exécution: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
