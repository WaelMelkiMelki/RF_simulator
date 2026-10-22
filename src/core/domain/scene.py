"""
Représentation d'une scène 3D pour la simulation RF.
Gère la géométrie, les matériaux et l'indexation spatiale.
"""

import logging
import numpy as np
import pyvista as pv
from typing import Optional, Any, Dict, List
import os

logger = logging.getLogger(__name__)


class Scene3D:
    """Représente une scène 3D avec géométrie et propriétés matérielles."""
    def propagate_materials_to_cells(self):
        """Propage les matériaux assignés aux cellules de la scène."""
        try:
            if not hasattr(self, 'mesh_material_mapping') or not self.mesh_material_mapping:
                logger.warning("Aucun mapping de matériaux à propager")
                return

            if self.mesh is None:
                logger.warning("Aucun mesh disponible pour la propagation")
                return

            logger.info(f"Propagation des matériaux aux cellules: {self.mesh_material_mapping}")
            # Vérifier si nous avons les informations d'origine
            if 'mesh_origin_id' not in self.mesh.cell_data:
                logger.warning("Aucune information d'origine des cellules")
                return

            # Créer un mapping des IDs d'origine vers les noms de matériaux
            origin_to_material = {}
            mesh_origins = self.mesh.field_data.get('mesh_origins', [])

            for i, origin_path in enumerate(mesh_origins):
                # Trouver le matériau assigné à ce mesh
                material_name = self.mesh_material_mapping.get(origin_path, "default")
                origin_to_material[i] = material_name

            # Appliquer les matériaux aux cellules
            material_names = []
            for origin_id in self.mesh.cell_data['mesh_origin_id']:
                material_names.append(origin_to_material.get(origin_id, "default"))

            # Stocker dans le mesh
            self.mesh.cell_data['material_name'] = material_names

            logger.info(f"Matériaux propagés à {len(material_names)} cellules")

        except Exception as e:
            logger.error(f"Erreur lors de la propagation des matériaux aux cellules: {e}")

    def __init__(self, data=None):
        self.data = None  # Données brutes (PolyData, MultiBlock, etc.)
        self.mesh = None  # Mesh PyVista traité (fusionné)
        # NOUVEAU: Dictionnaire des meshes individuels {nom: PolyData}
        self.meshes = {}
        self.materials = []  # Propriétés matérielles
        self.material_mapping = {}  # Mapping entre noms de matériaux et indices
        self.mesh_material_mapping = {}  # Ajoutez cette ligne
        self.spatial_index = None  # Index spatial pour optimisation
        self.material_properties = {}
        if data is not None:
            self.load_from_data(data)
        
    def load_from_data(self, data: Any):
        """Charge la scène à partir de données PyVista."""
        logger.info(f"Scene3D.load_from_data: Traitement des données de type {type(data)}")
        self.data = data
        self._process_data()
        # Construire l'index spatial pour optimisation des calculs RF
        self._build_spatial_index()
        logger.info("Scene3D.load_from_data: Données chargées avec succès")

    def _build_spatial_index(self):
        """
        Construit l'index spatial Octree pour optimiser les requêtes spatiales.
        
        Cet index permet d'accélérer significativement:
        - Les tests de ligne de vue (ray casting)
        - La détection d'obstacles sur les chemins de propagation
        - Les requêtes de voisinage
        """
        try:
            from core.domain.spatial_index import SpatialIndex
            
            if self.mesh is None:
                logger.debug("Scene3D._build_spatial_index: Pas de mesh disponible")
                return
            
            bounds = self.mesh.bounds  # (xmin, xmax, ymin, ymax, zmin, zmax)
            
            # Créer l'index spatial
            self.spatial_index = SpatialIndex(
                scene_bounds=bounds,
                max_depth=10,
                max_points_per_node=16
            )
            
            # Indexer les centres des cellules pour la détection d'obstacles
            if hasattr(self.mesh, 'cell_centers') and self.mesh.n_cells > 0:
                cell_centers = self.mesh.cell_centers()
                points = cell_centers.points
                
                for i, point in enumerate(points):
                    self.spatial_index.insert(
                        point.tolist(), 
                        {"cell_id": i, "type": "obstacle"}
                    )
                
                # Log des statistiques
                stats = self.spatial_index.get_statistics()
                logger.info(f"Scene3D: Index spatial construit - {len(points)} cellules indexées, "
                           f"{stats['total_nodes']} noeuds Octree, profondeur max: {stats['max_depth_reached']}")
            else:
                # Fallback: indexer les sommets
                points = self.mesh.points
                for i, point in enumerate(points):
                    self.spatial_index.insert(point.tolist(), {"point_id": i, "type": "vertex"})
                logger.info(f"Scene3D: Index spatial construit avec {len(points)} sommets")
                
        except ImportError:
            logger.debug("Scene3D._build_spatial_index: Module spatial_index non disponible")
            self.spatial_index = None
        except Exception as e:
            logger.warning(f"Scene3D._build_spatial_index: Erreur lors de la construction: {e}")
            self.spatial_index = None

    def _process_data(self):
        """Traite les données brutes pour créer un mesh utilisable."""
        if self.data is None:
            logger.warning("Scene3D._process_data: Aucune donnée à traiter")
            return
        # Vérifier le type de données
        if isinstance(self.data, pv.MultiBlock):
            logger.info("Scene3D._process_data: Format MultiBlock détecté (GLB/GLTF)...")
            self._process_multiblock_data()
        else:
            # Pour OBJ et autres formats simples
            logger.info("Scene3D._process_data: Format simple détecté")
            self.mesh = self.data
            logger.info(f"Scene3D._process_data: Mesh direct assigné: {self.mesh.n_points} points")

    def _process_multiblock_data(self):
        """Traite les données MultiBlock (GLB/GLTF)."""
        try:
            # Extraire les meshes individuels
            self._extract_individual_meshes_from_multiblock(self.data)
            # Fusionner tous les meshes pour le rendu global
            self.mesh = self._merge_multiblock_meshes(self.data)
            if self.mesh is not None:
                logger.info(f"Scene3D._process_multiblock_data: Mesh fusionné créé avec {self.mesh.n_points} points")
            else:
                logger.warning("Scene3D._process_multiblock_data: Aucun mesh fusionné créé")
        except Exception as e:
            logger.error(f"Scene3D._process_multiblock_data: Erreur lors du traitement: {e}")
            # Fallback: utiliser le premier mesh trouvé
            self.mesh = self._find_mesh(self.data)

    def _extract_individual_meshes_from_multiblock(self, multiblock_data: pv.MultiBlock):
        """
        Extrait les meshes individuels d'un MultiBlock GLTF.
        Version optimisée avec moins de logs.
        """
        try:
            logger.info("Scene3D: Extraction des meshes depuis MultiBlock...")
            self.meshes = {}
            self.mesh_material_mapping = {}
            def collect_meshes(block, path=""):
                if isinstance(block, pv.PolyData) and block.n_points > 0:
                    mesh_name = path if path else f"mesh_{len(self.meshes)}"
                    self.meshes[mesh_name] = block
                    self.mesh_material_mapping[mesh_name] = "default"
                elif isinstance(block, pv.MultiBlock):
                    for i in range(block.n_blocks):
                        sub_block = block[i]
                        child_path = f"{path}/Block_{i}" if path else f"Block_{i}"
                        collect_meshes(sub_block, child_path)
            collect_meshes(multiblock_data)
            logger.info(f"Scene3D: {len(self.meshes)} meshes individuels extraits")
        except Exception as e:
            logger.error(f"Scene3D._extract_individual_meshes_from_multiblock: Erreur: {e}")

    # --- NOUVEAU: Ajout de la méthode _merge_multiblock_meshes manquante ---
    def _merge_multiblock_meshes(self, multiblock_data: pv.MultiBlock):
        """Fusionne les meshes avec gestion mémoire optimisée."""
        try:
            meshes = []
            mesh_origins = []

            def collect_meshes(block, path=""):
                if isinstance(block, pv.PolyData) and block.n_points > 0:
                    # CRITIQUE: Utiliser copy() pour éviter les références mémoire
                    meshes.append(block.copy())
                    mesh_origins.append(path)
                elif isinstance(block, pv.MultiBlock):
                    for i in range(block.n_blocks):
                        sub_block = block[i]
                        child_path = f"{path}/Block_{i}" if path else f"Block_{i}"
                        collect_meshes(sub_block, child_path)

            collect_meshes(multiblock_data)

            if not meshes:
                logger.warning("Scene3D._merge_multiblock_meshes: Aucun mesh trouvé à fusionner")
                return None

            # Fusion progressive avec nettoyage mémoire
            combined_mesh = meshes[0].copy()
            origin_ids = np.zeros(meshes[0].n_cells, dtype=int)

            for i, mesh in enumerate(meshes[1:], start=1):
                n_cells_before = combined_mesh.n_cells
                combined_mesh = combined_mesh.merge(mesh)
                new_origin_ids = np.full(mesh.n_cells, i, dtype=int)
                origin_ids = np.concatenate([origin_ids, new_origin_ids])

                # CRITIQUE: Libération explicite de la mémoire
                del mesh
                if i % 5 == 0:
                    import gc
                    gc.collect()

            combined_mesh.cell_data['mesh_origin_id'] = origin_ids
            combined_mesh.field_data['mesh_origins'] = mesh_origins

            # Nettoyage final
            meshes.clear()
            logger.info(f"Scene3D._merge_multiblock_meshes: Fusion réussie. Mesh final combiné: {type(combined_mesh)} ({combined_mesh.n_points} points)")
            return combined_mesh

        except Exception as e:
            logger.error(f"Erreur fusion meshes: {e}")
            return None
    # --- FIN NOUVEAU ---

    def _find_mesh(self, data, path=""):
        """Trouve récursivement un mesh dans les données."""
        try:
            if isinstance(data, pv.PolyData) and data.n_points > 0:
                logger.info(f"Scene3D._find_mesh: Mesh trouvé à '{path}': type={type(data)}, n_points={data.n_points}")
                return data
            elif isinstance(data, pv.MultiBlock):
                logger.info(f"Scene3D._find_mesh: MultiBlock trouvé à '{path}', exploration de {len(data)} enfants...")
                # Parcourir les enfants du MultiBlock
                for i in range(data.n_blocks):
                    block = data[i]
                    child_path = f"{path}/Block_{i}" if path else f"Block_{i}"
                    mesh = self._find_mesh(block, child_path)
                    if mesh is not None:
                        return mesh
            else:
                logger.info(f"Scene3D._find_mesh: Exploration de l'enfant '{path}' (type={type(data)})")
        except Exception as e:
            logger.error(f"Scene3D._find_mesh: Erreur lors de l'exploration '{path}': {e}")
        return None

    # --- NOUVELLES MÉTHODES POUR L'INTERFACE ---
    def get_mesh_names(self) -> List[str]:
        """Retourne la liste des noms de meshes individuels."""
        return list(self.meshes.keys())
    
    def set_mesh_material(self, mesh_name: str, material_name: str):
        """
        Associe un matériau à un mesh.
        
        Args:
            mesh_name (str): Nom du mesh.
            material_name (str): Nom du matériau à associer.
        """
        if mesh_name in self.meshes:
            self.mesh_material_mapping[mesh_name] = material_name
            logger.info(f"Scene3D: Matériau '{material_name}' associé au mesh '{mesh_name}'")
        else:
            logger.warning(f"Scene3D.set_mesh_material: Mesh '{mesh_name}' non trouvé.")
            
    def get_mesh_material(self, mesh_name: str) -> Optional[str]:
        """
        Retourne le matériau associé à un mesh.
        
        Args:
            mesh_name (str): Nom du mesh.
            
        Returns:
            Optional[str]: Nom du matériau associé, ou None si non trouvé.
        """
        return self.mesh_material_mapping.get(mesh_name)

    # --- MÉTHODES EXISTANTES (non modifiées sauf si nécessaire) ---
    def get_pyvista_mesh(self) -> Optional[pv.PolyData]:
        """Retourne le mesh PyVista de la scène."""
        try:
            if self.mesh is not None:
                logger.info(f"Scene3D.get_pyvista_mesh: Mesh valide déjà présent ({self.mesh.n_points} points).")
                return self.mesh
            elif self.data is not None:
                logger.info(f"Scene3D.get_pyvista_mesh: Traitement des données brutes...")
                self._process_data()
                if self.mesh is not None:
                    logger.info(f"Scene3D.get_pyvista_mesh: Mesh traité ({self.mesh.n_points} points).")
                    return self.mesh
                else:
                    logger.warning("Scene3D.get_pyvista_mesh: Aucun mesh valide après traitement")
                    return None
            else:
                logger.warning("Scene3D.get_pyvista_mesh: Aucune donnée disponible")
                return None
        except Exception as e:
            logger.error(f"Scene3D.get_pyvista_mesh: Erreur lors de l'obtention du mesh: {e}")
            return None

    def get_bounds(self):
        """Retourne les limites de la scène."""
        try:
            mesh = self.get_pyvista_mesh()
            if mesh is not None:
                return mesh.bounds
            return [0, 1, 0, 1, 0, 1]  # Valeurs par défaut
        except Exception as e:
            logger.error(f"Scene3D.get_bounds: Erreur lors de l'obtention des limites: {e}")
            return [0, 1, 0, 1, 0, 1]

    def get_center(self):
        """Retourne le centre de la scène."""
        try:
            bounds = self.get_bounds()
            center = [
                (bounds[0] + bounds[1]) / 2,
                (bounds[2] + bounds[3]) / 2,
                (bounds[4] + bounds[5]) / 2
            ]
            return center
        except Exception as e:
            logger.error(f"Scene3D.get_center: Erreur lors du calcul du centre: {e}")
            return [0, 0, 0]

    def load_materials_from_mtl(self, mtl_file_path: str):
        """
        Charge les matériaux à partir d'un fichier MTL.
        
        Args:
            mtl_file_path (str): Chemin vers le fichier MTL
        """
        try:
            if not os.path.exists(mtl_file_path):
                logger.warning(f"Scene3D.load_materials_from_mtl: Fichier MTL non trouvé: {mtl_file_path}")
                return
                
            materials = {}
            current_material = None
            
            with open(mtl_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('newmtl'):
                        # Nouveau matériau
                        material_name = line.split()[1]
                        current_material = {
                            'name': material_name,
                            'Ka': [0.0, 0.0, 0.0],  # Couleur ambiante
                            'Kd': [0.0, 0.0, 0.0],  # Couleur diffuse
                            'Ks': [0.0, 0.0, 0.0],  # Couleur spéculaire
                            'Ns': 0.0,              # Exposant spéculaire
                            'd': 1.0,               # Opacité
                            'illum': 2              # Modèle d'illumination
                        }
                        materials[material_name] = current_material
                    elif line.startswith('Ka') and current_material:
                        # Couleur ambiante
                        values = line.split()[1:]
                        current_material['Ka'] = [float(v) for v in values]
                    elif line.startswith('Kd') and current_material:
                        # Couleur diffuse
                        values = line.split()[1:]
                        current_material['Kd'] = [float(v) for v in values]
                    elif line.startswith('Ks') and current_material:
                        # Couleur spéculaire
                        values = line.split()[1:]
                        current_material['Ks'] = [float(v) for v in values]
                    elif line.startswith('Ns') and current_material:
                        # Exposant spéculaire
                        current_material['Ns'] = float(line.split()[1])
                    elif line.startswith('d') and current_material:
                        # Opacité
                        current_material['d'] = float(line.split()[1])
                    elif line.startswith('illum') and current_material:
                        # Modèle d'illumination
                        current_material['illum'] = int(line.split()[1])
            
            # Convertir les matériaux en propriétés RF
            self._convert_materials_to_rf_properties(materials)
            logger.info(f"Scene3D.load_materials_from_mtl: {len(materials)} matériaux chargés depuis {mtl_file_path}")
            
        except Exception as e:
            logger.error(f"Scene3D.load_materials_from_mtl: Erreur lors du chargement du fichier MTL: {e}")

    def _convert_materials_to_rf_properties(self, materials: Dict):
        """
        Convertit les matériaux du format MTL en propriétés RF.
        
        Args:
            materials (Dict): Dictionnaire des matériaux au format MTL
        """
        try:
            # Mapping entre noms de matériaux MTL et propriétés RF
            material_mapping = {
                'concrete': {'permittivity': 4.5, 'conductivity': 0.01},
                'glass': {'permittivity': 7.0, 'conductivity': 0.0001},
                'wood': {'permittivity': 2.1, 'conductivity': 0.0005},
                'steel': {'permittivity': 1.0, 'conductivity': 1000000.0},
                'metal': {'permittivity': 1.0, 'conductivity': 1000000.0},
                'brick': {'permittivity': 4.0, 'conductivity': 0.02},
                'plastic': {'permittivity': 2.5, 'conductivity': 0.00001},
                'default': {'permittivity': 1.0, 'conductivity': 0.0}
            }
            
            self.materials = []
            self.material_mapping = {}
            
            for i, (name, mtl_props) in enumerate(materials.items()):
                # Trouver le matériau RF correspondant
                rf_props = None
                name_lower = name.lower()
                
                # Recherche par nom exact
                for key, props in material_mapping.items():
                    if key in name_lower:
                        rf_props = props
                        break
                
                # Si non trouvé, utiliser le matériau par défaut
                if rf_props is None:
                    rf_props = material_mapping['default']
                
                # Créer le matériau RF
                rf_material = {
                    'name': name,
                    'permittivity': rf_props['permittivity'],
                    'conductivity': rf_props['conductivity'],
                    'color': mtl_props.get('Kd', [0.5, 0.5, 0.5]),
                    'mtl_properties': mtl_props  # Conserver les propriétés MTL originales
                }
                
                self.materials.append(rf_material)
                self.material_mapping[name] = i
                
            logger.info(f"Scene3D._convert_materials_to_rf_properties: {len(self.materials)} matériaux RF créés")
            
        except Exception as e:
            logger.error(f"Scene3D._convert_materials_to_rf_properties: Erreur lors de la conversion: {e}")

    def enrich_mesh_with_materials(self, obj_file_path: str):
        """
        Enrichit le maillage avec les informations de matériaux à partir du fichier OBJ.
        
        Args:
            obj_file_path (str): Chemin vers le fichier OBJ
        """
        try:
            mesh = self.get_pyvista_mesh()
            if mesh is None:
                logger.warning("Scene3D.enrich_mesh_with_materials: Aucun mesh disponible")
                return
                
            # Vérifier si le mesh a déjà des données de groupe
            if 'GroupIds' not in mesh.cell_data:
                logger.info("Scene3D.enrich_mesh_with_materials: Création des groupes à partir du fichier OBJ")
                self._create_groups_from_obj(obj_file_path)
                
            # Si nous avons des groupes, associer les matériaux
            if 'GroupIds' in mesh.cell_data and len(self.material_mapping) > 0:
                logger.info("Scene3D.enrich_mesh_with_materials: Association des matériaux aux cellules")
                self._assign_materials_to_cells()
            else:
                logger.warning("Scene3D.enrich_mesh_with_materials: Pas de groupes ou de matériaux à associer")
                
        except Exception as e:
            logger.error(f"Scene3D.enrich_mesh_with_materials: Erreur lors de l'enrichissement: {e}")

    def _create_groups_from_obj(self, obj_file_path: str):
        """
        Crée des groupes à partir du fichier OBJ en analysant les directives 'usemtl' et 'g'.
        
        Args:
            obj_file_path (str): Chemin vers le fichier OBJ
        """
        try:
            if not os.path.exists(obj_file_path):
                logger.warning(f"Scene3D._create_groups_from_obj: Fichier OBJ non trouvé: {obj_file_path}")
                return
                
            mesh = self.get_pyvista_mesh()
            if mesh is None:
                return
                
            # Lire le fichier OBJ pour identifier les groupes
            face_groups = {}  # {group_name: [face_indices]}
            current_group = "default"
            current_material = "default"
            face_index = 0
            
            with open(obj_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('g ') or line.startswith('o '):
                        # Nouveau groupe/objet
                        group_name = line.split()[1] if len(line.split()) > 1 else "default"
                        current_group = group_name
                        if current_group not in face_groups:
                            face_groups[current_group] = []
                    elif line.startswith('usemtl'):
                        # Nouveau matériau
                        material_name = line.split()[1] if len(line.split()) > 1 else "default"
                        current_material = material_name
                        group_name = f"{current_group}_{current_material}"
                        if group_name not in face_groups:
                            face_groups[group_name] = []
                    elif line.startswith('f '):
                        # Face
                        group_name = f"{current_group}_{current_material}"
                        if group_name not in face_groups:
                            face_groups[group_name] = []
                        face_groups[group_name].append(face_index)
                        face_index += 1
            
            # Créer un tableau d'identifiants de groupe pour chaque cellule
            if mesh.n_cells == face_index:
                group_ids = np.zeros(mesh.n_cells, dtype=int)
                group_names = list(face_groups.keys())
                
                for i, (group_name, face_indices) in enumerate(face_groups.items()):
                    for face_idx in face_indices:
                        if face_idx < mesh.n_cells:
                            group_ids[face_idx] = i
                
                mesh.cell_data['GroupIds'] = group_ids
                mesh.field_data['GroupNames'] = group_names
                
                logger.info(f"Scene3D._create_groups_from_obj: {len(group_names)} groupes créés")
            else:
                logger.warning(f"Scene3D._create_groups_from_obj: Incohérence entre faces OBJ ({face_index}) et cellules mesh ({mesh.n_cells})")
                
        except Exception as e:
            logger.error(f"Scene3D._create_groups_from_obj: Erreur lors de la création des groupes: {e}")

    def _assign_materials_to_cells(self):
        """
        Associe les matériaux aux cellules du maillage en fonction des groupes.
        """
        try:
            mesh = self.get_pyvista_mesh()
            if mesh is None or 'GroupIds' not in mesh.cell_data:
                return
                
            group_ids = mesh.cell_data['GroupIds']
            group_names = mesh.field_data.get('GroupNames', [])
            
            # Créer un mapping entre groupes et matériaux
            material_ids = np.zeros(len(group_ids), dtype=int)
            
            for i, group_id in enumerate(group_ids):
                if group_id < len(group_names):
                    group_name = group_names[group_id]
                    # Extraire le nom du matériau du nom du groupe (format: groupe_materiel)
                    material_name = group_name.split('_')[-1] if '_' in group_name else group_name
                    material_id = self.material_mapping.get(material_name, 0)
                    material_ids[i] = material_id
                    
            mesh.cell_data['material_id'] = material_ids
            logger.info(f"Scene3D._assign_materials_to_cells: {len(np.unique(material_ids))} matériaux assignés à {len(material_ids)} cellules")
            
        except Exception as e:
            logger.error(f"Scene3D._assign_materials_to_cells: Erreur lors de l'assignation: {e}")

    def get_material_for_cell(self, cell_id: int) -> Optional[Dict]:
        """
        Retourne les propriétés du matériau pour une cellule donnée.
        Args:
            cell_id (int): Identifiant de la cellule
        Returns:
            Optional[Dict]: Propriétés du matériau ou None si non trouvé
        """
        try:
            if (self.mesh is None or 
                'material_name' not in self.mesh.cell_data or 
                cell_id >= len(self.mesh.cell_data['material_name'])):
                return None

            material_name = self.mesh.cell_data['material_name'][cell_id]

            # Récupérer les propriétés du matériau depuis la base de données
            from core.domain.material_properties import MATERIAL_DATABASE, get_material_by_name
            material_props = MATERIAL_DATABASE.get(material_name, get_material_by_name(material_name))

            if material_props:
                # Convertir en format attendu par le modèle RF
                return {
                    'name': material_props.name,
                    'attenuation': material_props.base_attenuation,
                    'conductivity': 0.0  # À compléter avec des valeurs réelles
                }

        except Exception as e:
            logger.error(f"Scene3D.get_material_for_cell: Erreur lors de la récupération du matériau: {e}")

        return None

    def ray_cast(self, start_point, end_point):
        """
        Calcule les intersections d'un rayon avec les cellules du mesh.
        Retourne les indices des cellules traversées et les points d'intersection.
        """
        mesh = self.get_pyvista_mesh()
        if mesh is None:
            return [], []
        # Utilise la méthode PyVista pour le ray tracing
        intersection_points, cell_ids = mesh.ray_trace(start_point, end_point, first_point=False)[:2]
        return cell_ids, intersection_points

    def load_mesh(self, mesh):
        """Compatibility entry point; use the same processing path as file loading."""
        self.load_from_data(mesh)

    def process_glb_data(self, data):
        self.load_from_data(data)

    def get_material_properties(self, name):
        return self.material_properties.get(name)
