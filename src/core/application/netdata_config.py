# src/core/application/netdata_config.py
"""
Configuration Architecture NETDATA INNOVATION
Définit l'architecture modulaire conforme aux spécifications.

ARCHITECTURE NETDATA - Séparation des couches :

🎨 PRESENTATION LAYER
├── cli.py                           # Interface ligne de commande
├── src/gui/main_window.py          # Fenêtre principale PyQt6
├── src/gui/widgets/                # Widgets d'interface utilisateur
│   ├── scene_viewer_3d_widget.py   # Widget de visualisation 3D (UI)
│   └── *_widget.py                 # Autres widgets UI
├── src/gui/adapters/               # Adaptateurs présentation
│   └── backend_adapter.py          # Adaptateur vers couche Application
└── src/core/application/config_manager.py  # Gestionnaire de configuration

🧠 APPLICATION LAYER  
├── src/core/application/simulation_orchestrator.py  # Orchestrateur principal
├── src/core/application/data_validator.py          # Validation des données
└── src/core/application/exporter.py                # Export des résultats

🔬 DOMAIN LAYER
├── 📡 Antenna Services
│   ├── src/core/domain/antenna_factory.py          # Factory d'antennes
│   └── src/core/domain/antenna.py                  # Classes d'antennes
├── 📶 RF Services  
│   ├── src/core/domain/rf_models.py               # Modèles de propagation
│   └── src/core/application/optimized_rf_calculator.py  # Calculateur RF
└── 🏗️ Scene Services
    ├── src/core/domain/scene.py                   # Gestion des scènes 3D
    ├── src/core/domain/material_properties.py     # Propriétés des matériaux
    └── src/core/domain/spatial_index.py           # Index spatial

⚙️ INFRASTRUCTURE LAYER
├── 💾 Data Access
│   ├── src/core/infrastructure/file_loader.py     # Chargement de fichiers
│   ├── src/core/infrastructure/cache_manager.py   # Gestion du cache
│   └── src/core/infrastructure/db_access.py       # Accès base de données
├── 🖥️ Compute Services
│   ├── src/core/infrastructure/parallel_engine.py      # Moteur parallèle
│   ├── src/core/infrastructure/grid_generator.py       # Générateur de grilles
│   └── src/core/infrastructure/performance_monitor.py  # Monitoring performance
└── 🌐 External Services
    ├── src/gui/widgets/visualization_engine.py    # Moteur de visualisation PyVista
    └── src/core/infrastructure/logging_service.py # Service de logging

FLUX DE DONNÉES NETDATA :
CLI/GUI → ORCHESTRATOR → DOMAIN SERVICES → INFRASTRUCTURE → EXTERNAL SERVICES
"""

import logging
import os

# Configuration des couches NETDATA
NETDATA_LAYERS = {
    "presentation": {
        "description": "Interface utilisateur et présentation",
        "components": [
            "cli.py",
            "src/gui/main_window.py", 
            "src/gui/widgets/scene_viewer_3d_widget.py",
            "src/gui/adapters/backend_adapter.py",
            "src/core/application/config_manager.py"
        ],
        "responsibilities": [
            "Interface utilisateur PyQt6/CLI",
            "Gestion des événements UI",
            "Layout et contrôles visuels", 
            "Communication avec Application Layer"
        ]
    },
    
    "application": {
        "description": "Logique métier et orchestration",
        "components": [
            "src/core/application/simulation_orchestrator.py",
            "src/core/application/data_validator.py", 
            "src/core/application/exporter.py"
        ],
        "responsibilities": [
            "Orchestration du workflow de simulation",
            "Validation des données d'entrée",
            "Export et sérialisation des résultats",
            "Coordination des services Domain"
        ]
    },
    
    "domain": {
        "description": "Services métier et logique RF",
        "components": [
            "src/core/domain/antenna_factory.py",
            "src/core/domain/antenna.py",
            "src/core/domain/rf_models.py",
            "src/core/application/optimized_rf_calculator.py",
            "src/core/domain/scene.py",
            "src/core/domain/material_properties.py",
            "src/core/domain/spatial_index.py"
        ],
        "responsibilities": [
            "Modèles de propagation RF",
            "Factory et types d'antennes",
            "Gestion des scènes 3D",
            "Calculs RF optimisés",
            "Propriétés des matériaux",
            "Index spatial pour optimisations"
        ]
    },
    
    "infrastructure": {
        "description": "Services techniques et externes", 
        "components": [
            "src/core/infrastructure/file_loader.py",
            "src/core/infrastructure/cache_manager.py",
            "src/core/infrastructure/db_access.py",
            "src/core/infrastructure/parallel_engine.py",
            "src/core/infrastructure/grid_generator.py", 
            "src/core/infrastructure/performance_monitor.py",
            "src/gui/widgets/visualization_engine.py",
            "src/core/infrastructure/logging_service.py"
        ],
        "responsibilities": [
            "Accès aux données et fichiers",
            "Gestion du cache intelligent",
            "Moteur de calcul parallèle",
            "Génération de grilles",
            "Monitoring des performances",
            "Visualisation PyVista/VTK haute performance",
            "Logging structuré"
        ]
    }
}

# Règles de dépendances NETDATA
DEPENDENCY_RULES = {
    "presentation_can_use": ["application"],
    "application_can_use": ["domain", "infrastructure"],
    "domain_can_use": ["infrastructure"],
    "infrastructure_can_use": [],  # Pas de dépendances vers les couches supérieures
    
    "forbidden_dependencies": [
        ("infrastructure", "domain"),
        ("infrastructure", "application"), 
        ("infrastructure", "presentation"),
        ("domain", "application"),
        ("domain", "presentation")
    ]
}

# Configuration des services NETDATA
NETDATA_SERVICES = {
    "visualization_engine": {
        "layer": "infrastructure",
        "file": "src/gui/widgets/visualization_engine.py",
        "class": "VisualizationEngine",
        "description": "Moteur de visualisation 3D haute performance PyVista/VTK",
        "interfaces": ["update_scene", "show_antenna_coverage", "performance_metrics"],
        "optimizations": ["GPU acceleration", "Smart caching", "Performance monitoring"]
    },
    
    "simulation_orchestrator": {
        "layer": "application", 
        "file": "src/core/application/simulation_orchestrator.py",
        "class": "SimulationOrchestrator",
        "description": "Orchestrateur principal du workflow de simulation",
        "phases": ["validation", "scene_setup", "rf_calculation", "export"],
        "dependencies": ["antenna_factory", "rf_calculator", "scene_3d", "exporter"]
    },
    
    "rf_calculator": {
        "layer": "application",
        "file": "src/core/application/optimized_rf_calculator.py", 
        "class": "OptimizedRFCalculator",
        "description": "Calculateur RF optimisé avec support parallèle",
        "optimizations": ["Parallel processing", "GPU compute", "Smart algorithms"],
        "models": ["FreeSpaceModel", "SimpleRayTracingModel"]
    }
}

# Métriques de performance NETDATA
PERFORMANCE_TARGETS = {
    "visualization": {
        "target_fps": 30,
        "max_render_time_ms": 33,
        "max_memory_usage_mb": 2048,
        "gpu_utilization_target": 0.7
    },
    
    "rf_calculation": {
        "max_calculation_time_s": 60,
        "parallel_efficiency_target": 0.8,
        "memory_efficiency_target": 0.9
    },
    
    "overall": {
        "startup_time_s": 5,
        "memory_footprint_mb": 512,
        "cpu_utilization_target": 0.6
    }
}

def validate_netdata_architecture():
    """Valide que l'architecture NETDATA est respectée."""
    logger = logging.getLogger(__name__)
    issues = []
    
    # Vérifier la présence des composants critiques
    for layer_name, layer_config in NETDATA_LAYERS.items():
        for component in layer_config["components"]:
            # Convertir les wildcards en vérifications de base
            if "*" in component:
                base_path = component.replace("*", "")
                if not os.path.exists(base_path.split("*")[0]):
                    issues.append(f"Répertoire manquant pour {component}")
            else:
                if not os.path.exists(component):
                    issues.append(f"Composant manquant: {component}")
    
    # Vérifier les services critiques
    critical_services = ["visualization_engine", "simulation_orchestrator"]
    for service_name in critical_services:
        if service_name in NETDATA_SERVICES:
            service_file = NETDATA_SERVICES[service_name]["file"]
            if not os.path.exists(service_file):
                issues.append(f"Service critique manquant: {service_file}")
    
    if issues:
        logger.error("Problèmes d'architecture NETDATA détectés:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    else:
        logger.info("Architecture NETDATA validée avec succès")
        return True

def get_netdata_component_info(component_name):
    """Retourne les informations d'un composant NETDATA.""" 
    for layer_name, layer_config in NETDATA_LAYERS.items():
        if any(component_name in comp for comp in layer_config["components"]):
            return {
                "layer": layer_name,
                "description": layer_config["description"],
                "responsibilities": layer_config["responsibilities"]
            }
    
    # Vérifier dans les services
    if component_name in NETDATA_SERVICES:
        return NETDATA_SERVICES[component_name]
    
    return None

def log_architecture_info():
    """Log les informations d'architecture NETDATA."""
    logger = logging.getLogger(__name__)
    
    logger.info("=== ARCHITECTURE NETDATA INNOVATION ===")
    
    for layer_name, layer_config in NETDATA_LAYERS.items():
        logger.info(f"\n📋 {layer_name.upper()} LAYER:")
        logger.info(f"   Description: {layer_config['description']}")
        logger.info(f"   Composants: {len(layer_config['components'])}")
        for resp in layer_config['responsibilities']:
            logger.info(f"   - {resp}")
    
    logger.info(f"\n🔧 Services configurés: {len(NETDATA_SERVICES)}")
    logger.info("=========================================")

if __name__ == "__main__":
    # Test de validation
    log_architecture_info()
    validate_netdata_architecture()
