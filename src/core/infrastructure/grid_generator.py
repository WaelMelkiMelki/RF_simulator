"""
Générateur de grille pour la simulation RF.
"""

import numpy as np
import pyvista as pv

class GridGenerator:
    """Générateur de grille pour les points de calcul."""

    @staticmethod
    def generate(bounds, resolution=1.0, height_levels=3, voxel_size=None):
        """
        Génère une grille de points basée sur les bounds du mesh.
        
        Args:
            bounds: Bornes du mesh [xmin, xmax, ymin, ymax, zmin, zmax]
            resolution: Résolution XY (step en mètres)
            height_levels: Nombre de niveaux Z (utilisé si voxel_size=None)
            voxel_size: Taille de voxel pour grille 3D volumétrique (prioritaire si fourni)
        
        Returns:
            list: Liste de points [x, y, z]
        """
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        
        if voxel_size is not None:
            # Mode volumétrique 3D avec densité uniforme
            print(f"GridGenerator: Génération de grille 3D volumétrique avec voxel_size={voxel_size}")
            # Calculer le nombre de steps en chaque direction
            nx = int((xmax - xmin) / voxel_size) + 1
            ny = int((ymax - ymin) / voxel_size) + 1
            nz = int((zmax - zmin) / voxel_size) + 1
            
            # Générer axes uniformes
            x = np.linspace(xmin, xmax, nx)
            y = np.linspace(ymin, ymax, ny)
            z = np.linspace(zmin, zmax, nz)
            
            # Créer grille 3D complète
            X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
            points = np.vstack([X.ravel(), Y.ravel(), Z.ravel()]).T.tolist()
            
            print(f"GridGenerator: Grille 3D volumétrique générée: {len(points)} points (nx={nx}, ny={ny}, nz={nz})")
            return points
        
        else:
            # Mode par défaut : Plans XY à des Z discrets
            print(f"GridGenerator: Génération de grille sur {height_levels} plans Z avec xy_step={resolution}")
            # Générer niveaux Z (même logique que avant)
            z_levels = np.linspace(zmin, zmax, height_levels)
            print(f"GridGenerator: Niveaux Z générés: {z_levels}")
            
            # Générer grille XY pour chaque Z
            x = np.arange(xmin, xmax + resolution, resolution)
            y = np.arange(ymin, ymax + resolution, resolution)
            X, Y = np.meshgrid(x, y)
            
            points = []
            for z in z_levels:
                for xi, yi in zip(X.ravel(), Y.ravel()):
                    points.append([xi, yi, z])
            
            print(f"GridGenerator: Grille générée avec {len(points)} points sur {height_levels} plans Z.")
            return points