# src/core/application/optimized_rf_calculator.py
"""
Calculateur RF optimisé pour la simulation de couverture.
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

class OptimizedRFCalculator:
    """
    Calculateur RF optimisé pour la simulation de couverture.
    """

    def __init__(self, scene, antennas, propagation_model):
        self.scene = scene
        self.antennas = antennas
        self.propagation_model = propagation_model

    def calculate_radiation_pattern(self, antenna):
        """
        Calcule le diagramme de rayonnement pour une antenne donnée.
        Retourne un dictionnaire contenant les points et les valeurs de couverture.
        """
        logger.info(f"OptimizedRFCalculator: Calcul du diagramme pour l'antenne {antenna.name}")
        
        # Générer une grille de points autour de l'antenne
        grid_points = self._generate_grid_around_antenna(antenna)
        signal_strengths = []

        for point in grid_points:
            loss = self.propagation_model.calculate_path_loss(
                antenna.position, point, self.scene, antenna.frequency
            )
            rssi = antenna.power_dbm - loss
            signal_strengths.append(rssi)

        logger.info(f"OptimizedRFCalculator: Calcul du diagramme terminé. {len(grid_points)} points calculés")
        return {
            "points": grid_points.tolist(),
            "values": signal_strengths
        }

    def _generate_grid_around_antenna(self, antenna):
        """
        Génère une grille de points autour de l'antenne pour le calcul de couverture.
        """
        x0, y0, z0 = antenna.position
        
        # Utiliser le coverage_radius de l'antenne ou la valeur par défaut
        radius = getattr(antenna, 'coverage_radius', 15.0)
        logger.debug(f"OptimizedRFCalculator._generate_grid_around_antenna: Utilisation du rayon {radius}m pour {antenna.name}")
        
        # Créer une grille sphérique autour de l'antenne
        num_points = int((2 * radius / 1.0) ** 3)
        if num_points > 10000:  # Limiter pour performance
            resolution = 1.0 * (num_points / 10000) ** (1/3)
        else:
            resolution = 1.0
            
        x = np.arange(x0 - radius, x0 + radius, resolution)
        y = np.arange(y0 - radius, y0 + radius, resolution)
        z = np.arange(z0 - radius/2, z0 + radius/2, resolution/2)
        
        # Créer une grille 3D
        xx, yy, zz = np.meshgrid(x, y, z)
        points = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])
        
        # Filtrer les points trop éloignés (intérieur d'une sphère)
        distances = np.sqrt((points[:, 0] - x0)**2 + (points[:, 1] - y0)**2 + (points[:, 2] - z0)**2)
        mask = distances <= radius
        filtered_points = points[mask]
        
        return filtered_points

    def calculate_coverage_grid_detailed(self, resolution=1.0):
        """
        Calcule une grille détaillée de couverture pour la heatmap.
        Retourne tous les points et leurs valeurs de signal.
        """
        logger.info(f"OptimizedRFCalculator: Calcul de la grille détaillée avec résolution {resolution}m")

        # Obtenir les bornes de la scène
        mesh = self.scene.get_pyvista_mesh()
        bounds = mesh.bounds
        logger.debug(f"DEBUG: Bornes de la scène utilisées: {bounds}")
        logger.debug(f"OptimizedRFCalculator: Bornes de la scène = {bounds}")

        # Générer une grille régulière avec la résolution donnée
        x = np.arange(bounds[0], bounds[1], resolution)
        y = np.arange(bounds[2], bounds[3], resolution)
        z = np.arange(bounds[4], bounds[5], resolution)

        logger.debug(f"OptimizedRFCalculator: Dimensions de la grille: {len(x)} x {len(y)} x {len(z)}")

        # Créer la grille 3D
        xx, yy, zz = np.meshgrid(x, y, z)
        grid_points = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])

        logger.info(f"OptimizedRFCalculator: Grille générée avec {len(grid_points)} points")

        # Calculer le signal pour chaque point
        signal_values = []
        valid_points = []

        # Ajouter des logs pour voir les valeurs extrêmes
        all_signal_values = []

        for i, point in enumerate(grid_points):
            total_signal = self._calculate_total_signal_at_point(point)
            all_signal_values.append(total_signal)

            # Log de progression détaillé
            if i % max(1, len(grid_points) // 10) == 0 and i > 0:  # Tous les 10%
                progress = (i / len(grid_points)) * 100
                current_min = np.min(all_signal_values)
                current_max = np.max(all_signal_values)
                current_mean = np.mean(all_signal_values)
                logger.debug(f"OptimizedRFCalculator: Progression {progress:.1f}% ({i}/{len(grid_points)}) - Min: {current_min:.2f}dBm, Max: {current_max:.2f}dBm, Moyenne: {current_mean:.2f}dBm")

            # CORRECTION: Utiliser un seuil plus réaliste
            if total_signal > -200:  # Seuil abaissé pour afficher les signaux faibles
                signal_values.append(total_signal)
                valid_points.append(point)

        logger.info(f"OptimizedRFCalculator: Calcul de la grille détaillée terminé")

        # Log des statistiques finales
        if len(all_signal_values) > 0:
            overall_min = np.min(all_signal_values)
            overall_max = np.max(all_signal_values)
            overall_mean = np.mean(all_signal_values)
            overall_std = np.std(all_signal_values)
            logger.info(f"OptimizedRFCalculator: Statistiques globales - Min: {overall_min:.2f}dBm, Max: {overall_max:.2f}dBm, Moyenne: {overall_mean:.2f}dBm, Écart-type: {overall_std:.2f}dBm")

            # Log des percentiles pour mieux comprendre la distribution
            percentiles = [5, 25, 50, 75, 95]
            for p in percentiles:
                value = np.percentile(all_signal_values, p)
                logger.info(f"OptimizedRFCalculator: Percentile {p}%: {value:.2f}dBm")

        logger.info(f"OptimizedRFCalculator: Points valides: {len(valid_points)}")

        if len(valid_points) > 0:
            min_val = np.min(signal_values)
            max_val = np.max(signal_values)
            mean_val = np.mean(signal_values)
            logger.info(f"OptimizedRFCalculator: Valeurs finales: Min={min_val:.2f}dBm, Max={max_val:.2f}dBm, Moyenne={mean_val:.2f}dBm")
        else:
            logger.warning("OptimizedRFCalculator: Aucun point valide trouvé")
            # Log des valeurs extrêmes même si aucun point n'est valide
            if len(all_signal_values) > 0:
                min_all = np.min(all_signal_values)
                max_all = np.max(all_signal_values)
                logger.warning(f"OptimizedRFCalculator: Même les meilleures valeurs sont inférieures au seuil: Min={min_all:.2f}dBm, Max={max_all:.2f}dBm")

        return {
            'points': valid_points,
            'values': signal_values
        }

    def _calculate_total_signal_at_point(self, point):
        """
        Calcule le signal total (somme de tous les signaux) à un point donné.
        """
        total_signal = -100  # Valeur par défaut très faible (presque zéro)
        signal_found = False
        
        for antenna in self.antennas:
            try:
                loss = self.propagation_model.calculate_path_loss(
                    antenna.position, point, self.scene, antenna.frequency
                )
                rssi = antenna.power_dbm - loss
                
                # Log détaillé pour chaque calcul
                logger.debug(f"OptimizedRFCalculator: Antenne {antenna.name} - Position: {antenna.position}, Point: {point}, Loss: {loss:.2f}dB, RSSI: {rssi:.2f}dBm")
                
                # Si c'est le premier signal valide, l'utiliser
                if not signal_found:
                    total_signal = rssi
                    signal_found = True
                else:
                    # Combiner les signaux (addition de puissances)
                    total_signal = self._combine_signals(total_signal, rssi)
                    
            except Exception as e:
                logger.debug(f"OptimizedRFCalculator: Erreur calcul signal pour {antenna.name}: {e}")
                continue
        
        logger.debug(f"OptimizedRFCalculator: Signal total au point {point}: {total_signal:.2f}dBm")
        return total_signal

    def _combine_signals(self, signal1, signal2):
        """
        Combine deux signaux (en dBm) de manière réaliste.
        """
        # Convertir de dBm en puissance linéaire, additionner, puis reconvertir en dBm
        try:
            # Pour éviter les problèmes avec des valeurs très négatives
            if signal1 < -90 and signal2 < -90:
                return max(signal1, signal2)  # Prendre le meilleur des deux mauvais signaux
            elif signal1 < -90:
                return signal2
            elif signal2 < -90:
                return signal1
            else:
                # Additionner les puissances (approximation simplifiée)
                p1_linear = 10 ** (signal1 / 10)
                p2_linear = 10 ** (signal2 / 10)
                p_total_linear = p1_linear + p2_linear
                if p_total_linear > 0:
                    combined = 10 * np.log10(p_total_linear)
                    return max(combined, -150)  # Limiter à -150 dBm minimum
                else:
                    return max(signal1, signal2)
        except:
            return max(signal1, signal2)