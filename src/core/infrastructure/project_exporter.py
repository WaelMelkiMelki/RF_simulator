"""
Module ProjectExporter pour l'export des projets NETDATA.
Partie de la couche Infrastructure - responsable de l'export des données de projet.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import xml.etree.ElementTree as ET
except ImportError:
    ET = None

logger = logging.getLogger(__name__)


class ProjectExporter:
    """
    Classe pour l'export des projets NETDATA vers différents formats.
    Fait partie de la couche Infrastructure - gère l'export des données de projet.
    """
    
    def __init__(self):
        """Initialise l'exporteur de projet."""
        self.supported_formats = ['json', 'xml', 'yaml']
        logger.info("ProjectExporter initialisé")
    
    def export_project(self, project_data: Dict[str, Any], export_path: str, 
                      format_type: str = 'json') -> bool:
        """
        Exporte les données du projet vers un fichier.
        
        Args:
            project_data: Données du projet à exporter
            export_path: Chemin de destination pour l'export
            format_type: Format d'export ('json', 'xml', 'yaml')
            
        Returns:
            bool: True si l'export a réussi, False sinon
        """
        try:
            if format_type not in self.supported_formats:
                logger.error(f"Format d'export non supporté: {format_type}")
                return False
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type == 'json':
                return self._export_json(project_data, export_file)
            elif format_type == 'xml':
                return self._export_xml(project_data, export_file)
            elif format_type == 'yaml':
                return self._export_yaml(project_data, export_file)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'export du projet: {e}")
            return False
    
    def _export_json(self, project_data: Dict[str, Any], export_file: Path) -> bool:
        """Exporte les données au format JSON."""
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Projet exporté au format JSON: {export_file}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'export JSON: {e}")
            return False
    
    def _export_xml(self, project_data: Dict[str, Any], export_file: Path) -> bool:
        """Exporte les données au format XML."""
        try:
            if ET is None:
                logger.error("Module XML non disponible")
                return False
            
            root = ET.Element("NetdataProject")
            self._dict_to_xml(project_data, root)
            
            tree = ET.ElementTree(root)
            tree.write(export_file, encoding='utf-8', xml_declaration=True)
            logger.info(f"Projet exporté au format XML: {export_file}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'export XML: {e}")
            return False
    
    def _export_yaml(self, project_data: Dict[str, Any], export_file: Path) -> bool:
        """Exporte les données au format YAML."""
        try:
            # Import conditionnel pour YAML
            import yaml
            
            with open(export_file, 'w', encoding='utf-8') as f:
                yaml.dump(project_data, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Projet exporté au format YAML: {export_file}")
            return True
        except ImportError:
            logger.error("Module YAML non disponible")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'export YAML: {e}")
            return False
    
    def _dict_to_xml(self, data: Any, parent: Any) -> None:
        """Convertit récursivement un dictionnaire en XML."""
        if isinstance(data, dict):
            for key, value in data.items():
                element = ET.SubElement(parent, str(key))
                self._dict_to_xml(value, element)
        elif isinstance(data, list):
            for item in data:
                element = ET.SubElement(parent, "item")
                self._dict_to_xml(item, element)
        else:
            parent.text = str(data)
    
    def get_supported_formats(self) -> list:
        """Retourne la liste des formats d'export supportés."""
        return self.supported_formats.copy()
    
    def validate_project_data(self, project_data: Dict[str, Any]) -> bool:
        """
        Valide la structure des données de projet avant export.
        
        Args:
            project_data: Données du projet à valider
            
        Returns:
            bool: True si les données sont valides, False sinon
        """
        try:
            required_fields = ['name', 'version', 'scene', 'antennas']
            
            for field in required_fields:
                if field not in project_data:
                    logger.error(f"Champ requis manquant: {field}")
                    return False
            
            logger.info("Données de projet validées avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la validation des données: {e}")
            return False
