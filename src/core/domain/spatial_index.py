# src/core/domain/spatial_index.py
"""
Indexation spatiale pour le RF Simulator 3D.
Implémente un Octree 3D pour organiser les objets de la scène et permettre
des requêtes spatiales rapides.
"""

import numpy as np
from typing import List, Tuple, Optional, Any, Dict

class BoundingBox:
    """Représente une boîte englobante 3D axis-aligned (AABB)."""
    
    def __init__(self, min_bound: List[float], max_bound: List[float]):
        """
        Initialise une boîte englobante.
        
        Args:
            min_bound: Coordonnées minimales [x, y, z]
            max_bound: Coordonnées maximales [x, y, z]
        """
        self.min = np.array(min_bound, dtype=np.float64)
        self.max = np.array(max_bound, dtype=np.float64)
        
    def contains_point(self, point: List[float]) -> bool:
        """
        Vérifie si un point est à l'intérieur de la boîte.
        
        Args:
            point: Coordonnées du point [x, y, z]
            
        Returns:
            bool: True si le point est dans la boîte
        """
        p = np.array(point, dtype=np.float64)
        return bool(np.all((self.min <= p) & (p <= self.max)))
        
    def intersects(self, other: 'BoundingBox') -> bool:
        """
        Vérifie si cette boîte intersecte une autre boîte.
        
        Args:
            other: Autre boîte englobante
            
        Returns:
            bool: True si les boîtes s'intersectent
        """
        return bool(
            np.all(self.min <= other.max) and 
            np.all(other.min <= self.max)
        )
        
    def get_center(self) -> np.ndarray:
        """
        Retourne le centre de la boîte.
        
        Returns:
            np.ndarray: Coordonnées du centre [x, y, z]
        """
        return (self.min + self.max) / 2.0
        
    def get_size(self) -> np.ndarray:
        """
        Retourne la taille (dx, dy, dz) de la boîte.
        
        Returns:
            np.ndarray: Taille de la boîte [dx, dy, dz]
        """
        return self.max - self.min

class OctreeNode:
    """Noeud d'un Octree 3D pour indexation spatiale."""
    
    def __init__(self, boundary: BoundingBox, capacity: int = 8, depth: int = 0, max_depth: int = 10):
        """
        Initialise un noeud de l'octree.
        
        Args:
            boundary: Boîte englobante du noeud
            capacity: Nombre maximum de points avant subdivision
            depth: Profondeur du noeud dans l'arbre
            max_depth: Profondeur maximale autorisée
        """
        # ✅ CORRECTION CRITIQUE : Vérifier que boundary est bien une BoundingBox
        if not isinstance(boundary, BoundingBox):
            raise TypeError("boundary doit être une instance de BoundingBox")
        if depth > max_depth:
            raise RecursionError(f"Profondeur maximale dépassée: {depth} > {max_depth}")
        self.boundary = boundary  # ✅ Attribut boundary correctement assigné
        self.capacity = capacity
        self.depth = depth
        self.max_depth = max_depth  # ✅ Nouvel attribut
        self.points: List[Tuple[List[float], Any]] = []  # Liste de tuples (point, data)
        self.children: List[Optional['OctreeNode']] = [None] * 8
        self.is_divided = False
        
    def subdivide(self):
        """Divise le noeud en 8 enfants."""
        # ✅ Protection contre la récursion infinie
        if self.is_divided or self.depth >= self.max_depth:
            return
        center = self.boundary.get_center()
        size = self.boundary.get_size()
        half_size = size / 2.0
        # Créer les 8 boîtes enfants
        for i in range(8):
            dx = half_size[0] if (i & 1) else -half_size[0]
            dy = half_size[1] if (i & 2) else -half_size[1]
            dz = half_size[2] if (i & 4) else -half_size[2]
            child_min = center + np.array([dx - half_size[0], dy - half_size[1], dz - half_size[2]])
            child_max = center + np.array([dx + half_size[0], dy + half_size[1], dz + half_size[2]])
            child_boundary = BoundingBox(child_min.tolist(), child_max.tolist())
            self.children[i] = OctreeNode(child_boundary, self.capacity, self.depth + 1, self.max_depth)
        self.is_divided = True
        points_to_redistribute = self.points[:]
        self.points = []  # Vider immédiatement
        for point, data in points_to_redistribute:
            self.insert(point, data)
            
    def insert(self, point: List[float], data: Any = None) -> bool:
        """
        Insère un point avec des données associées dans l'octree.
        
        Args:
            point: Un tuple ou array (x, y, z).
            data: Données associées au point.
            
        Returns:
            bool: True si l'insertion a réussi, False sinon.
        """
        # ✅ CORRECTION CRITIQUE : Vérifier que self.boundary existe
        if not hasattr(self, 'boundary') or self.boundary is None:
            raise AttributeError("OctreeNode n'a pas d'attribut 'boundary' valide")
        # ✅ Protection contre la récursion infinie
        if self.depth > self.max_depth:
            return False  # Ne pas subdiviser au-delà de la profondeur maximale
        # Vérifier si le point est dans les limites de ce noeud
        if not self.boundary.contains_point(point):
            return False
        # Si le noeud n'est pas subdivisé et a de la capacité
        if not self.is_divided and len(self.points) < self.capacity:
            self.points.append((point, data))
            return True
        # Sinon, subdiviser si ce n'est pas déjà fait ET si la profondeur le permet
        if not self.is_divided and self.depth < self.max_depth:
            self.subdivide()
        # Insérer dans l'enfant approprié (si subdivisé)
        if self.is_divided:
            for child in self.children:
                if child and child.insert(point, data):
                    return True
        # Si aucun enfant ne l'a pris (devrait rarement arriver)
        return False
        
    def query_range(self, range_box: BoundingBox) -> List[Tuple[List[float], Any]]:
        """
        Trouve tous les points dans une boîte donnée.
        
        Args:
            range_box: La boîte de requête.
            
        Returns:
            List[Tuple[List[float], Any]]: Liste de tuples (point, data) trouvés.
        """
        # ✅ CORRECTION CRITIQUE : Vérifier que self.boundary existe
        if not hasattr(self, 'boundary') or self.boundary is None:
            raise AttributeError("OctreeNode n'a pas d'attribut 'boundary' valide")
        # ✅ Protection contre la récursion infinie
        if self.depth > self.max_depth:
            return []
        found_points = []
        if not self.boundary.intersects(range_box):
            return found_points
        for point, data in self.points:
            if range_box.contains_point(point):
                found_points.append((point, data))
        if self.is_divided:
            for child in self.children:
                if child:
                    found_points.extend(child.query_range(range_box))
        return found_points
        
    def query_point(self, target_point: List[float], radius: float = 0.0) -> List[Tuple[List[float], Any, float]]:
        """
        Trouve le point le plus proche ou les points dans un rayon.
        
        Args:
            target_point: Le point cible (x, y, z).
            radius: Rayon de recherche. Si 0, retourne le point le plus proche.
            
        Returns:
            List[Tuple[List[float], Any, float]]: Liste de tuples (point, data, distance) trouvés.
        """
        # ✅ CORRECTION CRITIQUE : Vérifier que self.boundary existe
        if not hasattr(self, 'boundary') or self.boundary is None:
            raise AttributeError("OctreeNode n'a pas d'attribut 'boundary' valide")
        # ✅ Protection contre la récursion infinie
        if self.depth > self.max_depth:
            return []
        # Pour simplifier, on fait une recherche dans une boîte englobante
        # et on filtre par distance.
        p = np.array(target_point, dtype=np.float64)
        search_min = p - radius
        search_max = p + radius
        range_box = BoundingBox(search_min.tolist(), search_max.tolist())
        candidates = self.query_range(range_box)
        results = []
        for point, data in candidates:
            dist = float(np.linalg.norm(np.array(point, dtype=np.float64) - p))
            if dist <= radius or radius == 0.0:
                results.append((point, data, dist))
        if radius == 0.0 and results:
            results.sort(key=lambda x: x[2])
            return [results[0]]
        return results

class SpatialIndex:
    """
    Index spatial utilisant un Octree pour organiser les objets de la scène 3D.
    Permet des requêtes rapides comme "trouver les objets proches d'un point".
    """
    
    def __init__(self, scene_bounds: Optional[Tuple[float, float, float, float, float, float]] = None, 
                 max_depth: int = 10, max_points_per_node: int = 8):
        """
        Initialise l'index spatial.
        
        Args:
            scene_bounds: Les limites de la scène (x_min, x_max, y_min, y_max, z_min, z_max).
                         Si None, elles seront déterminées dynamiquement (plus complexe).
            max_depth: Profondeur maximale de l'octree.
            max_points_per_node: Nombre maximum de points par noeud avant subdivision.
        """
        if scene_bounds is None:
            # Par défaut, une grande boîte. Dans une vraie implémentation,
            # les bornes seraient déterminées à partir de la scène.
            scene_bounds = (-1000.0, 1000.0, -1000.0, 1000.0, -1000.0, 1000.0)
            
        self.bounds = BoundingBox(
            [scene_bounds[0], scene_bounds[2], scene_bounds[4]],  # min_bound
            [scene_bounds[1], scene_bounds[3], scene_bounds[5]]   # max_bound
        )
        self.max_depth = max_depth
        self.max_points_per_node = max_points_per_node
        # ✅ CORRECTION : Passer max_depth au noeud racine
        self.root = OctreeNode(self.bounds, self.max_points_per_node, 0, self.max_depth)
        
    def insert(self, point: List[float], data: Any = None):
        """
        Insère un point (et ses données) dans l'index spatial.
        
        Args:
            point: Un tuple ou array (x, y, z).
            data: Données associées au point (par exemple, un ID d'objet ou un triangle de mesh).
        """
        # ✅ CORRECTION CRITIQUE : Appeler insert sur le noeud racine
        return self.root.insert(point, data)
        
    def query_range(self, x_min: float, x_max: float, y_min: float, y_max: float, 
                   z_min: float, z_max: float) -> List[Tuple[List[float], Any]]:
        """
        Trouve tous les points dans une boîte donnée.
        
        Args:
            x_min, x_max, y_min, y_max, z_min, z_max: Limites de la boîte de requête.
            
        Returns:
            List[Tuple[List[float], Any]]: Liste de tuples (point, data) trouvés.
        """
        query_box = BoundingBox([x_min, y_min, z_min], [x_max, y_max, z_max])
        return self.root.query_range(query_box)
        
    def query_point(self, x: float, y: float, z: float, radius: float = 0.0) -> List[Tuple[List[float], Any, float]]:
        """
        Trouve le point le plus proche ou les points dans un rayon.
        
        Args:
            x, y, z: Coordonnées du point cible.
            radius: Rayon de recherche. Si 0, retourne le point le plus proche.
            
        Returns:
            List[Tuple[List[float], Any, float]]: Liste de tuples (point, data, distance) trouvés.
        """
        return self.root.query_point([x, y, z], radius)
        
    def get_statistics(self) -> Dict[str, Any]:
        """
        (Optionnel) Renvoie des statistiques sur l'octree (nombre de noeuds, profondeur, etc.).
        Utile pour le debugging ou l'optimisation.
        """
        def count_nodes(node: Optional[OctreeNode]) -> int:
            if node is None:
                return 0
            count = 1
            if node.is_divided:
                for child in node.children:
                    if child:
                        count += count_nodes(child)
            return count
            
        def get_max_depth(node: Optional[OctreeNode]) -> int:
            if node is None:
                return 0
            if not node.is_divided:
                return node.depth
            max_child_depth = 0
            for child in node.children:
                if child:
                    child_depth = get_max_depth(child)
                    max_child_depth = max(max_child_depth, child_depth)
            return max_child_depth
            
        return {
            "total_nodes": count_nodes(self.root),
            "max_depth_reached": get_max_depth(self.root),
            "max_depth_configured": self.max_depth,
            "points_per_node_limit": self.max_points_per_node,
            "root_points_count": len(self.root.points) if self.root else 0
        }

# Pour tester le module de manière isolée
if __name__ == '__main__':
    print("Test de l'indexation spatiale...")
    
    # Créer un index spatial
    spatial_index = SpatialIndex()
    print("✅ SpatialIndex créé")
    
    # Insérer quelques points
    spatial_index.insert([0, 0, 0], "point_origine")
    spatial_index.insert([1, 1, 1], "point_1")
    spatial_index.insert([2, 2, 2], "point_2")
    spatial_index.insert([10, 10, 10], "point_loin")
    print("✅ Points insérés")
    
    # Effectuer une requête
    results = spatial_index.query_point(0, 0, 0, radius=1.5)
    print(f"✅ Requête effectuée: {len(results)} résultats trouvés")
    
    # Afficher les statistiques
    stats = spatial_index.get_statistics()
    print(f"✅ Statistiques: {stats}")
    
    print("✅ Tests terminés avec succès")