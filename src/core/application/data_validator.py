# src/core/application/data_validator.py
"""
Module pour la validation des données d'entrée de la simulation.
Correspond à l'entité DataValidator du diagramme de classes.
"""

import logging
from typing import List, Any, Tuple

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)

class DataValidationError(Exception):
    """Exception levée lorsqu'une erreur de validation est détectée."""
    pass

class DataValidator:
    """
    Classe responsable de la validation des données d'entrée de la simulation.
    Vérifie la cohérence et l'intégrité des scènes, antennes, etc.
    """

    def __init__(self):
        """Initialise le validateur."""
        logger.debug("DataValidator initialisé.")

    def validate_scene(self, scene: Any) -> bool:
        """
        Valide un objet Scene3D.

        Args:
            scene (Any): L'objet Scene3D à valider.

        Returns:
            bool: True si la scène est valide.

        Raises:
            DataValidationError: Si la scène n'est pas valide.
        """
        logger.debug("Début de la validation de la scène.")
        
        if scene is None:
            raise DataValidationError("La scène ne doit pas être None.")
            
        # Vérifier si l'objet a une méthode get_pyvista_mesh
        if not hasattr(scene, 'get_pyvista_mesh'):
            raise DataValidationError("L'objet scène n'a pas la méthode 'get_pyvista_mesh'. Type invalide.")
        
        # Essayer d'obtenir le mesh
        try:
            mesh = scene.get_pyvista_mesh()
        except Exception as e:
            raise DataValidationError(f"Erreur lors de l'extraction du mesh de la scène: {e}")
            
        if mesh is None:
            raise DataValidationError("La scène n'a pas pu fournir un mesh valide.")
            
        # Vérifier que le mesh a des points
        if not hasattr(mesh, 'n_points'):
            raise DataValidationError("Le mesh de la scène n'a pas d'attribut 'n_points'.")
            
        if mesh.n_points <= 0:
            raise DataValidationError("Le mesh de la scène ne contient aucun point.")
            
        logger.info("Validation de la scène réussie.")
        return True

    def validate_antennas(self, antennas: List[Any]) -> bool:
        """
        Valide une liste d'objets antenne.

        Args:
            antennas (List[Any]): La liste des antennes à valider.

        Returns:
            bool: True si toutes les antennes sont valides.

        Raises:
            DataValidationError: Si une antenne n'est pas valide.
        """
        logger.debug(f"Début de la validation de {len(antennas)} antenne(s).")
        
        if not isinstance(antennas, list):
            raise DataValidationError("La liste des antennes doit être de type 'list'.")
            
        if len(antennas) == 0:
            logger.warning("La liste des antennes est vide.")
            # C'est une condition valide selon certains workflows, mais on logge un warning
            # Si c'est interdit, lever une exception ici.
            # raise DataValidationError("La liste des antennes ne doit pas être vide.")
            
        for i, antenna in enumerate(antennas):
            if antenna is None:
                raise DataValidationError(f"L'antenne à l'index {i} est None.")
                
            # Vérifier les attributs de base attendus
            required_attrs = ['name', 'position', 'frequency', 'power_dbm']
            for attr in required_attrs:
                if not hasattr(antenna, attr):
                    raise DataValidationError(f"L'antenne à l'index {i} n'a pas l'attribut requis '{attr}'.")
            
            # Valider le type de position (doit être un tuple ou liste de 3 nombres)
            pos = getattr(antenna, 'position')
            if not isinstance(pos, (tuple, list)) or len(pos) != 3:
                raise DataValidationError(f"La position de l'antenne {i} doit être un tuple ou une liste de 3 éléments.")
            if not all(isinstance(coord, (int, float)) for coord in pos):
                raise DataValidationError(f"Les coordonnées de la position de l'antenne {i} doivent être des nombres.")
                
            # Valider la fréquence (doit être un nombre positif)
            freq = getattr(antenna, 'frequency')
            if not isinstance(freq, (int, float)) or freq <= 0:
                raise DataValidationError(f"La fréquence de l'antenne {i} doit être un nombre positif.")
                
            # Valider la puissance (doit être un nombre)
            power = getattr(antenna, 'power_dbm')
            if not isinstance(power, (int, float)):
                raise DataValidationError(f"La puissance de l'antenne {i} doit être un nombre.")

        logger.info("Validation des antennes réussie.")
        return True

    def validate_propagation_model_config(self, config: dict) -> bool:
        """
        Valide la configuration du modèle de propagation.
        Args:
            config (dict): Configuration du modèle de propagation.
        Returns:
            bool: True si la configuration est valide.
        Raises:
            DataValidationError: Si la configuration est invalide.
        """
        model_name = config.get("propagation_model")
        model_config = config.get("propagation_model_config", {})
        
        if model_name == "simple_ray_tracing":
            max_reflections = model_config.get("max_reflections")
            if not isinstance(max_reflections, int) or max_reflections < 0:
                raise DataValidationError("Le nombre maximal de réflexions doit être un entier positif ou zéro.")
        elif model_name == "material_aware":
            max_reflections = model_config.get("max_reflections", 3)
            if not isinstance(max_reflections, int) or max_reflections < 0:
                raise DataValidationError("Le nombre maximal de réflexions doit être un entier positif ou zéro.")
            environment = model_config.get("environment")
            if environment not in ["residential", "office", "commercial"]:
                raise DataValidationError("L'environnement doit être 'residential', 'office' ou 'commercial'.")
        elif model_name == "material_aware":
            max_reflections = model_config.get("max_reflections", 3)
            if not isinstance(max_reflections, int) or max_reflections < 0:
                raise DataValidationError("Le nombre maximum de réflexions doit être un entier positif.")
        return True

    def validate_all(self, scene: Any, antennas: List[Any], config: dict = None) -> bool:
        """
        Valide l'ensemble des données (scène, antennes et configuration).
        Args:
            scene (Any): L'objet Scene3D.
            antennas (List[Any]): La liste des antennes.
            config (dict, optional): Configuration de la simulation.
        Returns:
            bool: True si toutes les données sont valides.
        """
        logger.debug("Début de la validation globale (scène + antennes + configuration).")
        self.validate_scene(scene)
        self.validate_antennas(antennas)
        if config is not None:
            self.validate_propagation_model_config(config)
        logger.info("Validation globale réussie.")
        return True

# Exemple d'utilisation (facultatif, pour documentation)
if __name__ == "__main__":
    # Cet exemple nécessiterait d'instancier des objets Scene3D et Antenna factices
    # pour une démonstration autonome, ce qui est complexe ici.
    pass