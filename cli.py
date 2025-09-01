#!/usr/bin/env python3
"""
Interface Ligne de Commande - NETDATA INNOVATION
COUCHE PRESENTATION - CLI Handler

Interface en ligne de commande pour le simulateur RF NETDATA.
Permet l'exécution de simulations sans interface graphique.
"""
import argparse
import logging
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_logging(level=logging.INFO):
    """Configure le logging pour l'interface CLI."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('rf_simulator_cli.log')
        ]
    )

def main():
    """Point d'entrée principal de l'interface CLI."""
    parser = argparse.ArgumentParser(
        description='RF Simulator NETDATA INNOVATION - Interface Ligne de Commande'
    )
    
    parser.add_argument(
        '--scene', '-s',
        type=str,
        help='Chemin vers le fichier de scène 3D'
    )
    
    parser.add_argument(
        '--output', '-o', 
        type=str,
        default='simulation_results',
        help='Répertoire de sortie pour les résultats'
    )
    
    parser.add_argument(
        '--frequency', '-f',
        type=float,
        default=2400.0,
        help='Fréquence en MHz (défaut: 2400)'
    )
    
    parser.add_argument(
        '--power', '-p',
        type=float,
        default=20.0,
        help='Puissance en dBm (défaut: 20)'
    )
    
    parser.add_argument(
        '--resolution', '-r',
        type=float,
        default=1.0,
        help='Résolution de grille en mètres (défaut: 1.0)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mode verbeux'
    )
    
    args = parser.parse_args()
    
    # Configuration du logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("=== RF SIMULATOR NETDATA CLI ===")
    
    try:
        # Import des composants NETDATA après configuration du path
        from core.application.simulation_orchestrator import SimulationOrchestrator
        from core.application.netdata_config import validate_netdata_architecture
        
        # Validation de l'architecture
        if not validate_netdata_architecture():
            logger.error("Architecture NETDATA non conforme - arrêt")
            return 1
        
        # Configuration de la simulation
        config = {
            'frequency': args.frequency,
            'power': args.power,
            'grid_resolution': args.resolution,
            'output_path': args.output
        }
        
        logger.info(f"Configuration: {config}")
        
        # Création de l'orchestrateur
        orchestrator = SimulationOrchestrator()
        
        # Chargement de la scène si spécifiée
        if args.scene:
            logger.info(f"Chargement de la scène: {args.scene}")
            scene = orchestrator.load_scene(args.scene)
            if not scene:
                logger.error("Erreur de chargement de la scène")
                return 1
        
        # Lancement de la simulation
        logger.info("Démarrage de la simulation...")
        results = orchestrator.run_simulation(config)
        
        if results:
            logger.info("Simulation terminée avec succès")
            logger.info(f"Résultats sauvegardés dans: {args.output}")
            return 0
        else:
            logger.error("Échec de la simulation")
            return 1
            
    except Exception as e:
        logger.error(f"Erreur CLI: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
