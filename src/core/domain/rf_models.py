# src/core/domain/rf_models.py
"""
Modèles de propagation RF pour la simulation.
"""

import numpy as np
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class PropagationStrategy(ABC):
    @abstractmethod
    def calculate_path_loss(self, tx_pos, rx_pos, scene, frequency, antenna=None):
        pass

    def calculate_effective_gain(self, tx_pos, direction, scene, frequency, antenna, max_distance=100.0):
        """Calcule le gain effectif dans une direction, intégrant pattern et propagation."""
        import numpy as np
        rx_pos = np.array(tx_pos) + max_distance * np.array(direction)
        path_loss = self.calculate_path_loss(tx_pos, rx_pos, scene, frequency, antenna)
        pattern_gain = antenna.calculate_radiation_pattern(theta=np.arccos(direction[2]), phi=np.arctan2(direction[1], direction[0])) if antenna else 1.0
        return 10 * np.log10(pattern_gain) - path_loss  # Gain en dB

class FreeSpaceModel(PropagationStrategy):
    def calculate_path_loss(self, tx_pos, rx_pos, scene, frequency, antenna=None):
        import numpy as np
        distance = np.linalg.norm(np.array(tx_pos) - np.array(rx_pos))
        
        # Log de la distance calculée
        logger.debug(f"FreeSpaceModel: Distance calculée entre {tx_pos} et {rx_pos}: {distance:.2f}m")
        
        if distance == 0:
            logger.debug("FreeSpaceModel: Distance nulle, perte = 0")
            return 0
            
        # CORRECTION: Calcul correct de la perte en espace libre (formule de Friis)
        # Formule: PL = 20*log10(d) + 20*log10(f) + 20*log10(4π/c) + PL0
        # où PL0 = 20*log10(λ/(4π)) = 20*log10(c/(4π*f)) = 20*log10(3e8/(4π*2.4e9)) ≈ -147.55 dB
        c = 3e8  # Vitesse de la lumière en m/s
        pl0 = 20 * np.log10(c / (4 * np.pi * frequency))  # Constante de perte de base
        loss = 20 * np.log10(distance) - pl0  # Formule corrigée
        
        logger.debug(f"FreeSpaceModel: Perte calculée: {loss:.2f}dB (distance={distance:.2f}m, fréquence={frequency/1e9}GHz)")
        return loss

class MaterialAwareModel(PropagationStrategy):
    def __init__(self, max_reflections=3):
        self.max_reflections = max_reflections

    def calculate_path_loss(self, tx_pos, rx_pos, scene, frequency, antenna=None):
        """
        Calcule la perte de signal en tenant compte des matériaux traversés.
        """
        try:
            # Calculer le chemin direct
            direct_loss = self._calculate_direct_path_with_materials(tx_pos, rx_pos, scene, frequency)
            
            if direct_loss is not None:
                logger.debug(f"MaterialAwareModel: Chemin direct trouvé avec perte: {direct_loss:.2f}dB")
                return direct_loss
                
            # Si pas de chemin direct, calculer les chemins réfléchis
            reflected_loss = self._calculate_reflected_paths_with_materials(tx_pos, rx_pos, scene, frequency)
            
            if reflected_loss is not None:
                logger.debug(f"MaterialAwareModel: Chemin réfléchi trouvé avec perte: {reflected_loss:.2f}dB")
                return reflected_loss
                
            # Perte par défaut très élevée si aucun chemin n'est trouvé
            default_loss = 1000
            logger.debug(f"MaterialAwareModel: Aucun chemin trouvé, perte par défaut: {default_loss}dB")
            return default_loss
            
        except Exception as e:
            logger.error(f"MaterialAwareModel: Erreur lors du calcul de la perte: {e}")
            return 1000

    def _calculate_direct_path_with_materials(self, tx_pos, rx_pos, scene, frequency):
        """
        Calcule la perte pour le chemin direct en tenant compte des matériaux traversés.
        """
        try:
            # Utiliser le ray casting pour trouver les cellules traversées
            cell_ids, intersection_points = scene.ray_cast(tx_pos, rx_pos)
            
            if len(cell_ids) == 0:
                # Pas d'obstacle, chemin direct
                distance = np.linalg.norm(np.array(rx_pos) - np.array(tx_pos))
                return self._free_space_loss(distance, frequency)
            
            # Calculer la perte en tenant compte des matériaux
            total_loss = 0.0
            current_pos = np.array(tx_pos)
            
            for i, cell_id in enumerate(cell_ids):
                # Position d'intersection
                intersection_pos = np.array(intersection_points[i]) if i < len(intersection_points) else np.array(rx_pos)
                
                # Distance dans l'air (avant le matériau)
                air_distance = np.linalg.norm(intersection_pos - current_pos)
                total_loss += self._free_space_loss(air_distance, frequency)
                
                # Obtenir les propriétés du matériau
                material = scene.get_material_for_cell(cell_id)
                if material:
                    # Utiliser l'atténuation du matériau
                    attenuation_per_meter = material.get('attenuation', 0.0)
                    # Calculer la distance traversée dans le matériau (approximation)
                    material_thickness = 0.1  # Épaisseur moyenne en mètres
                    # Calculer la perte dans le matériau
                    material_loss = attenuation_per_meter * material_thickness
                    total_loss += material_loss
                    logger.debug(f"MaterialAwareModel: Traversée du matériau '{material['name']}' - Perte: {material_loss:.2f}dB")
                
                # Mettre à jour la position courante
                current_pos = intersection_pos
                
            # Ajouter la distance restante jusqu'au récepteur
            final_distance = np.linalg.norm(np.array(rx_pos) - current_pos)
            total_loss += self._free_space_loss(final_distance, frequency)
            
            return total_loss
            
        except Exception as e:
            logger.error(f"MaterialAwareModel._calculate_direct_path_with_materials: Erreur: {e}")
            # Fallback sur le modèle de base
            distance = np.linalg.norm(np.array(rx_pos) - np.array(tx_pos))
            return self._free_space_loss(distance, frequency)

    def _calculate_reflected_paths_with_materials(self, tx_pos, rx_pos, scene, frequency):
        """
        Calcule les chemins réfléchis en tenant compte des matériaux.
        """
        try:
            # Pour l'instant, retourner une approximation simple
            distance = np.linalg.norm(np.array(rx_pos) - np.array(tx_pos))
            reflected_distance = distance * 1.2  # Chemin légèrement plus long dû aux réflexions
            base_loss = self._free_space_loss(reflected_distance, frequency)
            
            # Ajouter une pénalité pour les réflexions
            reflection_penalty = 3.0  # dB par réflexion approximative
            return base_loss + reflection_penalty
            
        except Exception as e:
            logger.error(f"MaterialAwareModel._calculate_reflected_paths_with_materials: Erreur: {e}")
            return None

    def _free_space_loss(self, distance, frequency):
        import numpy as np
        if distance <= 0:
            return 0
        # CORRECTION: Utiliser la formule correcte de perte en espace libre
        c = 3e8  # Vitesse de la lumière en m/s
        pl0 = 20 * np.log10(c / (4 * np.pi * frequency))  # Constante de perte de base
        loss = 20 * np.log10(distance) - pl0
        logger.debug(f"MaterialAwareModel._free_space_loss: Distance={distance:.2f}m, Fréquence={frequency/1e9}GHz, Perte={loss:.2f}dB")
        return loss

class SimpleRayTracingModel(PropagationStrategy):
    """Modèle de ray tracing simplifié pour la simulation RF avec prise en compte de la géométrie."""
    
    def __init__(self, max_reflections=2):
        self.max_reflections = max_reflections
    
    def calculate_path_loss(self, tx_pos, rx_pos, scene, frequency, antenna=None):
        """
        Calcule la perte de signal avec ray tracing simplifié.
        """
        try:
            # Calcul de base avec la distance
            distance = np.linalg.norm(np.array(tx_pos) - np.array(rx_pos))
            base_loss = self._free_space_loss(distance, frequency)
            
            # Ajouter des facteurs liés à la géométrie si la scène le permet
            if hasattr(scene, 'get_obstruction_factor'):
                obstruction_factor = scene.get_obstruction_factor(tx_pos, rx_pos)
                base_loss += obstruction_factor
            
            logger.debug(f"SimpleRayTracingModel: Perte calculée: {base_loss:.2f}dB (distance={distance:.2f}m)")
            return base_loss
            
        except Exception as e:
            logger.error(f"SimpleRayTracingModel: Erreur lors du calcul: {e}")
            # Fallback sur espace libre
            distance = np.linalg.norm(np.array(tx_pos) - np.array(rx_pos))
            return self._free_space_loss(distance, frequency)
    
    def _free_space_loss(self, distance, frequency):
        import numpy as np
        if distance <= 0:
            return 0
        c = 3e8  # Vitesse de la lumière en m/s
        pl0 = 20 * np.log10(c / (4 * np.pi * frequency))
        loss = 20 * np.log10(distance) - pl0
        return loss