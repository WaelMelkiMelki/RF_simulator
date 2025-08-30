#!/usr/bin/env python3
"""
Script pour préparer l'environnement de test du RF Simulator 3D.
Étapes :
1. Chargement de la configuration via ConfigManager
2. Chargement de la scène 3D via FileLoader
3. Création d'antennes via AntennaFactory
4. Intégration avec BackendAdapter
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au chemin Python
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def prepare_test_environment():
    """Prépare l'environnement de test complet."""
    print("=== Préparation de l'environnement de test ===")
    
    # 1. Test de ConfigManager
    print("\n1. Test de ConfigManager...")
    try:
        from core.application.config_manager import ConfigManager
        
        # Tester avec YAML
        yaml_config_path = project_root / "config" / "test_config.yaml"
        if yaml_config_path.exists():
            config_manager = ConfigManager(str(yaml_config_path))
            print(f"✅ ConfigManager chargé depuis {yaml_config_path}")
            print(f"   Projet: {config_manager.get_project_info()['name']}")
            print(f"   Modèle: {config_manager.get_simulation_config()['model']}")
        else:
            print("⚠️  Fichier de configuration YAML non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur avec ConfigManager: {e}")
    
    # 2. Test de FileLoader
    print("\n2. Test de FileLoader...")
    try:
        from core.infrastructure.file_loader import FileLoader
        
        obj_file_path = project_root / "data" / "test_scene.obj"
        if obj_file_path.exists():
            loader = FileLoader()
            scene_data = loader.load_file(str(obj_file_path))
            print(f"✅ FileLoader a chargé {obj_file_path}")
            print(f"   Type de données: {type(scene_data)}")
        else:
            print("⚠️  Fichier de scène OBJ non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur avec FileLoader: {e}")
    
    # 3. Test d'AntennaFactory
    print("\n3. Test d'AntennaFactory...")
    try:
        from core.domain.antenna_factory import AntennaFactory
        
        factory = AntennaFactory()
        
        # Configuration des antennes
        wifi_config = {
            "name": "Test WiFi Antenna",
            "position": [0, 0, 1],
            "frequency": "2.4GHz",
            "power_dbm": 20.0,
            "ssid": "TestNetwork"
        }
        
        # Créer une antenne WiFi
        wifi_antenna = factory.create_antenna("wifi", wifi_config)
        print(f"✅ AntennaFactory a créé une antenne WiFi")
        print(f"   Nom: {wifi_antenna.name}")
        print(f"   Position: {wifi_antenna.position}")
        print(f"   Fréquence: {wifi_antenna.frequency} Hz")
        print(f"   SSID: {wifi_antenna.ssid}")
        
    except Exception as e:
        print(f"❌ Erreur avec AntennaFactory: {e}")
    
    # 4. Test de BackendAdapter
    print("\n4. Test de BackendAdapter...")
    try:
        # Vérifier si le fichier existe
        backend_adapter_path = project_root / "src" / "gui" / "adapters" / "backend_adapter.py"
        if backend_adapter_path.exists():
            print("✅ BackendAdapter existe")
            # On pourrait tester plus en profondeur si nécessaire
        else:
            print("❌ BackendAdapter non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur avec BackendAdapter: {e}")
    
    print("\n=== Fin de la préparation de l'environnement ===")

if __name__ == "__main__":
    # Créer les dossiers nécessaires
    config_dir = Path("config")
    data_dir = Path("data")
    config_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)
    
    prepare_test_environment()
