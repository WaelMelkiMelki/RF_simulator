# src/core/application/config_manager.py
"""
Configuration Manager pour le RF Simulator 3D.
Responsable du chargement, de la validation et de la fourniture 
des paramètres de configuration à l'application.
Correspond à l'entité CONFIG du diagramme de classes.
"""

import json
import yaml
import os
from typing import Dict, Any, Optional


class ConfigValidationError(Exception):
    """Exception levée lorsqu'une erreur de validation de configuration est détectée."""
    pass

class ConfigManager:
    """
    Gère la configuration de l'application.
    Peut charger des fichiers YAML/JSON et les valider.
    Fournit les paramètres à SimulationOrchestrator.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le ConfigManager.
        
        Args:
            config_path: Chemin vers le fichier de configuration (YAML ou JSON)
        """
        self.config_path = config_path
        self.config_data = {}
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Charge un fichier de configuration (YAML ou JSON).
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Dict: Données de configuration chargées
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si le format n'est pas supporté
            ConfigValidationError: Si la configuration est invalide
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")
            
        _, ext = os.path.splitext(config_path)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                if ext.lower() in ['.yaml', '.yml']:
                    self.config_data = yaml.safe_load(file)
                elif ext.lower() == '.json':
                    self.config_data = json.load(file)
                else:
                    raise ValueError(f"Format de configuration non supporté: {ext}")
                    
            self.validate_config()
            return self.config_data
            
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Erreur de parsing YAML: {e}")
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Erreur de parsing JSON: {e}")
        except Exception as e:
            raise ConfigValidationError(f"Erreur lors du chargement de la configuration: {e}")
    
    def validate_config(self) -> bool:
        """
        Valide la configuration chargée.
        
        Returns:
            bool: True si la configuration est valide
            
        Raises:
            ConfigValidationError: Si la configuration est invalide
        """
        if not self.config_data:
            raise ConfigValidationError("Aucune donnée de configuration chargée")
            
        # Vérifier les sections obligatoires
        required_sections = ['project', 'simulation']
        for section in required_sections:
            if section not in self.config_data:
                raise ConfigValidationError(f"Section requise manquante dans la configuration: {section}")
                
        # Vérifier les champs obligatoires dans project
        project_required = ['name', 'author']
        for field in project_required:
            if field not in self.config_data.get('project', {}):
                raise ConfigValidationError(f"Champ project requis manquant: {field}")
                
        # Vérifier les champs obligatoires dans simulation
        simulation_required = ['model', 'resolution']
        for field in simulation_required:
            if field not in self.config_data.get('simulation', {}):
                raise ConfigValidationError(f"Champ simulation requis manquant: {field}")
                
        # Valider le modèle de propagation
        model = self.config_data['simulation']['model']
        valid_models = ['free_space', 'ray_tracing']
        if model not in valid_models:
            raise ConfigValidationError(f"Modèle de propagation non supporté: {model}. Modèles valides: {valid_models}")
            
        # Valider la résolution
        resolution = self.config_data['simulation']['resolution']
        if not isinstance(resolution, (int, float)) or resolution <= 0:
            raise ConfigValidationError("La résolution doit être un nombre positif")
            
        return True
    
    def get_simulation_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration pour la simulation.
        
        Returns:
            Dict: Configuration de simulation
        """
        return self.config_data.get('simulation', {})
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        Récupère les informations du projet.
        
        Returns:
            Dict: Informations du projet
        """
        return self.config_data.get('project', {})
    
    def get_antennas_config(self) -> list:
        """
        Récupère la configuration des antennes.
        
        Returns:
            list: Configuration des antennes
        """
        return self.config_data.get('antennas', [])
    
    def get_export_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration d'export.
        
        Returns:
            Dict: Configuration d'export
        """
        return self.config_data.get('export', {})
    
    def get_full_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration complète.
        
        Returns:
            Dict: Configuration complète
        """
        return self.config_data
    
    def save_config(self, config_path: str) -> None:
        """
        Sauvegarde la configuration actuelle dans un fichier.
        
        Args:
            config_path: Chemin vers le fichier de sauvegarde
        """
        _, ext = os.path.splitext(config_path)
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as file:
            if ext.lower() in ['.yaml', '.yml']:
                yaml.dump(self.config_data, file, default_flow_style=False, allow_unicode=True)
            elif ext.lower() == '.json':
                json.dump(self.config_data, file, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Format de configuration non supporté pour la sauvegarde: {ext}")

# Exemple de configuration (pour documentation)
EXAMPLE_CONFIG = {
    "project": {
        "name": "Simulation RF Example",
        "author": "RF Team",
        "description": "Exemple de configuration pour simulation RF",
        "scene_file": "path/to/scene.glb"
    },
    "simulation": {
        "model": "free_space",  # ou "ray_tracing"
        "resolution": 1.0,      # en mètres
        "frequency": 2.4e9,     # en Hz (optionnel, peut être dans les antennes)
        "output_formats": ["csv", "vtk"]
    },
    "antennas": [
        {
            "type": "wifi",
            "name": "WiFi Antenna 1",
            "position": {"x": 0, "y": 0, "z": 1},
            "frequency": 2.4e9,
            "power_dbm": 20.0,
            "ssid": "MyNetwork"
        }
    ],
    "export": {
        "auto_export": True,
        "output_dir": "./results",
        "formats": ["csv", "vtk", "png"]
    }
}

if __name__ == "__main__":
    # Exemple d'utilisation
    print("ConfigManager - Module de gestion de configuration")
    print("Pour utiliser ce module, importez ConfigManager dans votre code.")