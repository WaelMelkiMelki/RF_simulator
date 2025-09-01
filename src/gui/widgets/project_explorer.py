# src/gui/widgets/project_explorer.py
"""
Widget pour explorer et gérer la structure du projet en cours.
Affiche une arborescence des éléments (scène, antennes, résultats).
"""

import sys
import os
from pathlib import Path

# Ajout du chemin src si nécessaire
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QHeaderView, QMenu, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

class ProjectExplorer(QWidget):
    """
    Arbre de structure du projet affichant les éléments clés.
    Permet la navigation et la gestion des éléments du projet.
    """
    
    # Signaux émis par le ProjectExplorer
    scene_selected = pyqtSignal(object)      # Émis quand une scène est sélectionnée
    antenna_selected = pyqtSignal(object)    # Émis quand une antenne est sélectionnée
    result_selected = pyqtSignal(object)     # Émis quand un résultat est sélectionné
    item_double_clicked = pyqtSignal(object) # Émis quand un item est double-cliqué
    
    def __init__(self, backend_adapter=None, parent=None):
        """
        Initialise l'explorateur de projet.
        
        Args:
            backend_adapter: Adaptateur backend pour interaction
            parent: Widget parent Qt
        """
        super().__init__(parent)
        self.backend_adapter = backend_adapter
        self.parent_window = parent
        self.current_project = None
        self.scene_items = []      # Liste des items de scène
        self.antenna_items = []    # Liste des items d'antenne
        self.result_items = []     # Liste des items de résultat
        
        self.init_ui()
        self.setup_context_menus()
        self.populate_initial_tree()
        
    def init_ui(self):
        """Initialise l'interface utilisateur de l'explorateur de projet."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer l'arbre du projet
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("📁 Projet")
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Style harmonisé avec ResultsDashboard
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: #f7f7fa;
                padding: 8px;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
        """)
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7fa;
            }
        """)
        
        layout.addWidget(self.tree)
        
    def setup_context_menus(self):
        """Configure les menus contextuels pour les différents types d'items."""
        # Menu contextuel pour la racine du projet
        self.project_menu = QMenu(self)
        self.project_menu.addAction("➕ Ajouter Scène", self.add_scene)
        self.project_menu.addAction("➕ Ajouter Antenne", self.add_antenna)
        self.project_menu.addSeparator()
        self.project_menu.addAction("🔄 Actualiser", self.refresh_tree)
        self.project_menu.addAction("🗑️ Fermer Projet", self.close_project)
        
        # Menu contextuel pour les scènes
        self.scene_menu = QMenu(self)
        self.scene_menu.addAction("👁️ Afficher", self.show_scene)
        self.scene_menu.addAction("✏️ Propriétés", self.edit_scene_properties)
        self.scene_menu.addSeparator()
        self.scene_menu.addAction("🗑️ Supprimer", self.remove_scene)
        
        # Menu contextuel pour les antennes
        self.antenna_menu = QMenu(self)
        self.antenna_menu.addAction("📡 Sélectionner", self.select_antenna)
        self.antenna_menu.addAction("✏️ Propriétés", self.edit_antenna_properties)
        self.antenna_menu.addSeparator()
        self.antenna_menu.addAction("🗑️ Supprimer", self.remove_antenna)
        
        # Menu contextuel pour les résultats
        self.result_menu = QMenu(self)
        self.result_menu.addAction("📊 Afficher", self.show_result)
        self.result_menu.addAction("📤 Exporter", self.export_result)
        self.result_menu.addSeparator()
        self.result_menu.addAction("🗑️ Supprimer", self.remove_result)
        
    def populate_initial_tree(self):
        """
        Remplit l'arbre avec la structure de base du projet.
        """
        try:
            # Effacer l'arbre existant
            self.tree.clear()
            
            # Créer l'item racine du projet
            self.project_root = QTreeWidgetItem(self.tree, ["🏠 Mon Projet"])
            self.project_root.setExpanded(True)
            self.project_root.setData(0, Qt.ItemDataRole.UserRole, "project_root")
            
            # Créer les catégories principales
            self.scenes_category = QTreeWidgetItem(self.project_root, ["🌍 Scènes 3D"])
            self.scenes_category.setData(0, Qt.ItemDataRole.UserRole, "scenes_category")
            self.scenes_category.setExpanded(True)
            
            self.antennas_category = QTreeWidgetItem(self.project_root, ["📡 Antennes"])
            self.antennas_category.setData(0, Qt.ItemDataRole.UserRole, "antennas_category")
            self.antennas_category.setExpanded(True)
            
            self.results_category = QTreeWidgetItem(self.project_root, ["📊 Résultats"])
            self.results_category.setData(0, Qt.ItemDataRole.UserRole, "results_category")
            self.results_category.setExpanded(True)
            
            # Ajouter des placeholders si nécessaire
            if not self.scene_items:
                placeholder = QTreeWidgetItem(self.scenes_category, ["(Aucune scène)"])
                placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
                
            if not self.antenna_items:
                placeholder = QTreeWidgetItem(self.antennas_category, ["(Aucune antenne)"])
                placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
                
            if not self.result_items:
                placeholder = QTreeWidgetItem(self.results_category, ["(Aucun résultat)"])
                placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
                
            # Développer l'arbre
            self.tree.expandAll()
            
            print("ProjectExplorer.populate_initial_tree: Arbre initial rempli")
            
        except Exception as e:
            error_msg = f"Erreur lors du remplissage de l'arbre initial: {e}"
            print(f"ProjectExplorer.populate_initial_tree: {error_msg}")
            self.show_error(error_msg)
    
    def populate_tree(self):
        """
        Remplit l'arbre avec les données réelles du projet.
        Cette méthode est appelée quand un projet est chargé.
        """
        try:
            # Effacer les listes d'items
            self.scene_items.clear()
            self.antenna_items.clear()
            self.result_items.clear()
            
            # Effacer les catégories existantes
            self.scenes_category.takeChildren()
            self.antennas_category.takeChildren()
            self.results_category.takeChildren()
            
            # Ajouter les scènes (si backend disponible)
            if self.backend_adapter and hasattr(self.backend_adapter, 'get_scenes'):
                scenes = self.backend_adapter.get_scenes()
                for scene in scenes:
                    self.add_scene_item(scene)
                    
            # Ajouter les antennes (si backend disponible)
            if self.backend_adapter and hasattr(self.backend_adapter, 'get_antennas'):
                antennas = self.backend_adapter.get_antennas()
                for antenna in antennas:
                    self.add_antenna_item(antenna)
                    
            # Ajouter les résultats (si backend disponible)
            if self.backend_adapter and hasattr(self.backend_adapter, 'get_results'):
                results = self.backend_adapter.get_results()
                for result in results:
                    self.add_result_item(result)
                    
            print("ProjectExplorer.populate_tree: Arbre rempli avec les données du projet")
            
        except Exception as e:
            error_msg = f"Erreur lors du remplissage de l'arbre: {e}"
            print(f"ProjectExplorer.populate_tree: {error_msg}")
            self.show_error(error_msg)
    
    def add_scene_item(self, scene_data):
        """
        Ajoute un item de scène à l'arbre.
        
        Args:
            scene_data: Données de la scène à ajouter
        """
        try:
            # Créer l'item
            scene_name = getattr(scene_data, 'name', 'Scène Inconnue')
            scene_item = QTreeWidgetItem(self.scenes_category, [f"🌍 {scene_name}"])
            scene_item.setData(0, Qt.ItemDataRole.UserRole, "scene")
            scene_item.setData(0, Qt.ItemDataRole.UserRole + 1, scene_data)
            
            # Ajouter à la liste
            self.scene_items.append(scene_item)
            
            # Mettre à jour le placeholder
            self._update_placeholders()
            
            print(f"ProjectExplorer.add_scene_item: Scène '{scene_name}' ajoutée")
            
        except Exception as e:
            error_msg = f"Erreur lors de l'ajout de la scène: {e}"
            print(f"ProjectExplorer.add_scene_item: {error_msg}")
            self.show_error(error_msg)
    
    def add_antenna_item(self, antenna_data):
        """
        Ajoute un item d'antenne à l'arbre.
        
        Args:
            antenna_data: Données de l'antenne à ajouter
        """
        try:
            # Créer l'item
            antenna_name = getattr(antenna_data, 'name', 'Antenne Inconnue')
            antenna_type = getattr(antenna_data, 'type', 'N/A')
            antenna_item = QTreeWidgetItem(self.antennas_category, [f"📡 {antenna_name} ({antenna_type})"])
            antenna_item.setData(0, Qt.ItemDataRole.UserRole, "antenna")
            antenna_item.setData(0, Qt.ItemDataRole.UserRole + 1, antenna_data)
            
            # Ajouter à la liste
            self.antenna_items.append(antenna_item)
            
            # Mettre à jour le placeholder
            self._update_placeholders()
            
            print(f"ProjectExplorer.add_antenna_item: Antenne '{antenna_name}' ajoutée")
            
        except Exception as e:
            error_msg = f"Erreur lors de l'ajout de l'antenne: {e}"
            print(f"ProjectExplorer.add_antenna_item: {error_msg}")
            self.show_error(error_msg)
    
    def add_result_item(self, result_data):
        """
        Ajoute un item de résultat à l'arbre.
        
        Args:
            result_data: Données du résultat à ajouter
        """
        try:
            # Créer l'item
            result_name = getattr(result_data, 'name', 'Résultat Inconnu')
            timestamp = getattr(result_data, 'timestamp', 'N/A')
            result_item = QTreeWidgetItem(self.results_category, [f"📊 {result_name} ({timestamp})"])
            result_item.setData(0, Qt.ItemDataRole.UserRole, "result")
            result_item.setData(0, Qt.ItemDataRole.UserRole + 1, result_data)
            
            # Ajouter à la liste
            self.result_items.append(result_item)
            
            # Mettre à jour le placeholder
            self._update_placeholders()
            
            print(f"ProjectExplorer.add_result_item: Résultat '{result_name}' ajouté")
            
        except Exception as e:
            error_msg = f"Erreur lors de l'ajout du résultat: {e}"
            print(f"ProjectExplorer.add_result_item: {error_msg}")
            self.show_error(error_msg)
    
    def _update_placeholders(self):
        """Met à jour les placeholders dans les catégories."""
        try:
            # Mettre à jour le placeholder des scènes
            if self.scenes_category.childCount() == 0:
                placeholder = QTreeWidgetItem(self.scenes_category, ["(Aucune scène)"])
                placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            elif self.scenes_category.child(0).text(0) == "(Aucune scène)":
                self.scenes_category.takeChild(0)
                
            # Mettre à jour le placeholder des antennes
            if self.antennas_category.childCount() == 0:
                placeholder = QTreeWidgetItem(self.antennas_category, ["(Aucune antenne)"])
                placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            elif self.antennas_category.child(0).text(0) == "(Aucune antenne)":
                self.antennas_category.takeChild(0)
                
            # Mettre à jour le placeholder des résultats
            if self.results_category.childCount() == 0:
                placeholder = QTreeWidgetItem(self.results_category, ["(Aucun résultat)"])
                placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            elif self.results_category.child(0).text(0) == "(Aucun résultat)":
                self.results_category.takeChild(0)
                
        except Exception as e:
            print(f"ProjectExplorer._update_placeholders: Erreur: {e}")
    
    def on_item_clicked(self, item, column):
        """
        Gestionnaire appelé quand un item est cliqué.
        
        Args:
            item: Item cliqué
            column: Colonne cliquée
        """
        try:
            item_type = item.data(0, Qt.ItemDataRole.UserRole)
            item_data = item.data(0, Qt.ItemDataRole.UserRole + 1)
            
            print(f"ProjectExplorer.on_item_clicked: Item cliqué - Type: {item_type}")
            
            # Émettre le signal approprié selon le type d'item
            if item_type == "scene" and item_data:
                self.scene_selected.emit(item_data)
            elif item_type == "antenna" and item_data:
                self.antenna_selected.emit(item_data)
            elif item_type == "result" and item_data:
                self.result_selected.emit(item_data)
                
        except Exception as e:
            error_msg = f"Erreur lors du clic sur l'item: {e}"
            print(f"ProjectExplorer.on_item_clicked: {error_msg}")
            self.show_error(error_msg)
    
    def on_item_double_clicked(self, item, column):
        """
        Gestionnaire appelé quand un item est double-cliqué.
        
        Args:
            item: Item double-cliqué
            column: Colonne double-cliquée
        """
        try:
            item_type = item.data(0, Qt.ItemDataRole.UserRole)
            item_data = item.data(0, Qt.ItemDataRole.UserRole + 1)
            
            print(f"ProjectExplorer.on_item_double_clicked: Item double-cliqué - Type: {item_type}")
            
            # Émettre le signal de double-clic
            self.item_double_clicked.emit(item_data)
            
            # Actions spécifiques selon le type
            if item_type == "scene":
                self.show_scene()
            elif item_type == "antenna":
                self.select_antenna()
            elif item_type == "result":
                self.show_result()
                
        except Exception as e:
            error_msg = f"Erreur lors du double-clic sur l'item: {e}"
            print(f"ProjectExplorer.on_item_double_clicked: {error_msg}")
            self.show_error(error_msg)
    
    def show_context_menu(self, position):
        """
        Affiche le menu contextuel approprié selon l'item sélectionné.
        
        Args:
            position: Position du clic droit
        """
        try:
            # Obtenir l'item sous le curseur
            item = self.tree.itemAt(position)
            if not item:
                return
                
            item_type = item.data(0, Qt.ItemDataRole.UserRole)
            
            # Afficher le menu approprié
            if item_type == "project_root":
                self.project_menu.exec(self.tree.viewport().mapToGlobal(position))
            elif item_type == "scene":
                self.scene_menu.exec(self.tree.viewport().mapToGlobal(position))
            elif item_type == "antenna":
                self.antenna_menu.exec(self.tree.viewport().mapToGlobal(position))
            elif item_type == "result":
                self.result_menu.exec(self.tree.viewport().mapToGlobal(position))
            elif item_type in ["scenes_category", "antennas_category", "results_category"]:
                # Pour les catégories, afficher un menu limité
                category_menu = QMenu(self)
                if item_type == "scenes_category":
                    category_menu.addAction("➕ Ajouter Scène", self.add_scene)
                elif item_type == "antennas_category":
                    category_menu.addAction("➕ Ajouter Antenne", self.add_antenna)
                elif item_type == "results_category":
                    category_menu.addAction("➕ Ajouter Résultat", lambda: None)  # Placeholder
                    
                category_menu.exec(self.tree.viewport().mapToGlobal(position))
                
        except Exception as e:
            error_msg = f"Erreur lors de l'affichage du menu contextuel: {e}"
            print(f"ProjectExplorer.show_context_menu: {error_msg}")
            self.show_error(error_msg)
    
    # --- Actions du menu contextuel ---
    
    def add_scene(self):
        """Ajoute une nouvelle scène au projet."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            file_filter = "Fichiers 3D (*.obj *.stl *.ply *.gltf *.glb);;Tous les fichiers (*)"
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Importer Scène 3D",
                "",
                file_filter
            )
            
            if file_path and os.path.exists(file_path):
                # Si backend disponible, charger la scène
                if self.backend_adapter:
                    self.backend_adapter.load_scene(file_path)
                    self.show_info(f"Scène chargée: {os.path.basename(file_path)}")
                else:
                    # Sinon, ajouter un item factice
                    fake_scene = type('FakeScene', (), {
                        'name': os.path.basename(file_path),
                        'path': file_path
                    })()
                    self.add_scene_item(fake_scene)
                    self.show_info(f"Scène ajoutée: {os.path.basename(file_path)}")
                    
        except Exception as e:
            error_msg = f"Erreur lors de l'ajout de la scène: {e}"
            print(f"ProjectExplorer.add_scene: {error_msg}")
            self.show_error(error_msg)
    
    def add_antenna(self):
        """Ajoute une nouvelle antenne au projet."""
        try:
            # Créer une antenne factice pour le test
            fake_antenna = type('FakeAntenna', (), {
                'name': 'Nouvelle Antenne',
                'type': 'WiFi',
                'frequency': '2.4 GHz',
                'power_dbm': 20.0,
                'position': [0, 0, 1]
            })()
            
            # Si backend disponible, ajouter via le backend
            if self.backend_adapter:
                self.backend_adapter.add_antenna("wifi", {
                    "name": "Nouvelle Antenne",
                    "position": [0, 0, 1],
                    "frequency": "2.4GHz",
                    "power_dbm": 20.0
                })
                self.show_info("Antenne ajoutée via le backend")
            else:
                # Sinon, ajouter directement à l'arbre
                self.add_antenna_item(fake_antenna)
                self.show_info("Antenne ajoutée")
                
        except Exception as e:
            error_msg = f"Erreur lors de l'ajout de l'antenne: {e}"
            print(f"ProjectExplorer.add_antenna: {error_msg}")
            self.show_error(error_msg)
    
    def show_scene(self):
        """Affiche la scène sélectionnée."""
        try:
            # Obtenir l'item sélectionné
            selected_items = self.tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                item_type = item.data(0, Qt.ItemDataRole.UserRole)
                item_data = item.data(0, Qt.ItemDataRole.UserRole + 1)
                
                if item_type == "scene" and item_data:
                    # Émettre le signal de sélection de scène
                    self.scene_selected.emit(item_data)
                    self.show_info(f"Affichage de la scène: {getattr(item_data, 'name', 'Inconnue')}")
                else:
                    self.show_warning("Veuillez sélectionner une scène")
            else:
                self.show_warning("Aucun élément sélectionné")
                
        except Exception as e:
            error_msg = f"Erreur lors de l'affichage de la scène: {e}"
            print(f"ProjectExplorer.show_scene: {error_msg}")
            self.show_error(error_msg)
    
    def select_antenna(self):
        """Sélectionne l'antenne sélectionnée."""
        try:
            # Obtenir l'item sélectionné
            selected_items = self.tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                item_type = item.data(0, Qt.ItemDataRole.UserRole)
                item_data = item.data(0, Qt.ItemDataRole.UserRole + 1)
                
                if item_type == "antenna" and item_data:
                    # Émettre le signal de sélection d'antenne
                    self.antenna_selected.emit(item_data)
                    self.show_info(f"Antenne sélectionnée: {getattr(item_data, 'name', 'Inconnue')}")
                else:
                    self.show_warning("Veuillez sélectionner une antenne")
            else:
                self.show_warning("Aucun élément sélectionné")
                
        except Exception as e:
            error_msg = f"Erreur lors de la sélection de l'antenne: {e}"
            print(f"ProjectExplorer.select_antenna: {error_msg}")
            self.show_error(error_msg)
    
    def show_result(self):
        """Affiche le résultat sélectionné."""
        try:
            # Obtenir l'item sélectionné
            selected_items = self.tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                item_type = item.data(0, Qt.ItemDataRole.UserRole)
                item_data = item.data(0, Qt.ItemDataRole.UserRole + 1)
                
                if item_type == "result" and item_data:
                    # Émettre le signal de sélection de résultat
                    self.result_selected.emit(item_data)
                    self.show_info(f"Affichage du résultat: {getattr(item_data, 'name', 'Inconnu')}")
                else:
                    self.show_warning("Veuillez sélectionner un résultat")
            else:
                self.show_warning("Aucun élément sélectionné")
                
        except Exception as e:
            error_msg = f"Erreur lors de l'affichage du résultat: {e}"
            print(f"ProjectExplorer.show_result: {error_msg}")
            self.show_error(error_msg)
    
    def edit_scene_properties(self):
        """Édite les propriétés de la scène sélectionnée."""
        self.show_info("Édition des propriétés de la scène (fonctionnalité à implémenter)")
        
    def edit_antenna_properties(self):
        """Édite les propriétés de l'antenne sélectionnée."""
        self.show_info("Édition des propriétés de l'antenne (fonctionnalité à implémenter)")
        
    def export_result(self):
        """Exporte le résultat sélectionné."""
        self.show_info("Export du résultat (fonctionnalité à implémenter)")
        
    def remove_scene(self):
        """Supprime la scène sélectionnée."""
        try:
            selected_items = self.tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                item_type = item.data(0, Qt.ItemDataRole.UserRole)
                
                if item_type == "scene":
                    # Confirmation
                    reply = QMessageBox.question(
                        self, 
                        "Confirmation", 
                        "Êtes-vous sûr de vouloir supprimer cette scène ?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # Retirer de la liste et de l'arbre
                        if item in self.scene_items:
                            self.scene_items.remove(item)
                        self.scenes_category.removeChild(item)
                        self._update_placeholders()
                        self.show_info("Scène supprimée")
                else:
                    self.show_warning("Veuillez sélectionner une scène")
            else:
                self.show_warning("Aucun élément sélectionné")
                
        except Exception as e:
            error_msg = f"Erreur lors de la suppression de la scène: {e}"
            print(f"ProjectExplorer.remove_scene: {error_msg}")
            self.show_error(error_msg)
    
    def remove_antenna(self):
        """Supprime l'antenne sélectionnée."""
        try:
            selected_items = self.tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                item_type = item.data(0, Qt.ItemDataRole.UserRole)
                
                if item_type == "antenna":
                    # Confirmation
                    reply = QMessageBox.question(
                        self, 
                        "Confirmation", 
                        "Êtes-vous sûr de vouloir supprimer cette antenne ?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # Retirer de la liste et de l'arbre
                        if item in self.antenna_items:
                            self.antenna_items.remove(item)
                        self.antennas_category.removeChild(item)
                        self._update_placeholders()
                        self.show_info("Antenne supprimée")
                else:
                    self.show_warning("Veuillez sélectionner une antenne")
            else:
                self.show_warning("Aucun élément sélectionné")
                
        except Exception as e:
            error_msg = f"Erreur lors de la suppression de l'antenne: {e}"
            print(f"ProjectExplorer.remove_antenna: {error_msg}")
            self.show_error(error_msg)
    
    def remove_result(self):
        """Supprime le résultat sélectionné."""
        try:
            selected_items = self.tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                item_type = item.data(0, Qt.ItemDataRole.UserRole)
                
                if item_type == "result":
                    # Confirmation
                    reply = QMessageBox.question(
                        self, 
                        "Confirmation", 
                        "Êtes-vous sûr de vouloir supprimer ce résultat ?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # Retirer de la liste et de l'arbre
                        if item in self.result_items:
                            self.result_items.remove(item)
                        self.results_category.removeChild(item)
                        self._update_placeholders()
                        self.show_info("Résultat supprimé")
                else:
                    self.show_warning("Veuillez sélectionner un résultat")
            else:
                self.show_warning("Aucun élément sélectionné")
                
        except Exception as e:
            error_msg = f"Erreur lors de la suppression du résultat: {e}"
            print(f"ProjectExplorer.remove_result: {error_msg}")
            self.show_error(error_msg)
    
    def refresh_tree(self):
        """Actualise l'arbre du projet."""
        try:
            self.populate_tree()
            self.show_info("Arbre du projet actualisé")
        except Exception as e:
            error_msg = f"Erreur lors de l'actualisation: {e}"
            print(f"ProjectExplorer.refresh_tree: {error_msg}")
            self.show_error(error_msg)
    
    def close_project(self):
        """Ferme le projet actuel."""
        try:
            # Confirmation
            reply = QMessageBox.question(
                self, 
                "Confirmation", 
                "Êtes-vous sûr de vouloir fermer le projet ?\nLes modifications non sauvegardées seront perdues.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Effacer l'arbre
                self.tree.clear()
                
                # Réinitialiser les listes
                self.scene_items.clear()
                self.antenna_items.clear()
                self.result_items.clear()
                
                # Recréer l'arbre initial
                self.populate_initial_tree()
                
                self.show_info("Projet fermé")
                
        except Exception as e:
            error_msg = f"Erreur lors de la fermeture du projet: {e}"
            print(f"ProjectExplorer.close_project: {error_msg}")
            self.show_error(error_msg)
    
    # --- Méthodes utilitaires ---
    
    def show_error(self, message):
        """
        Affiche un message d'erreur.
        
        Args:
            message: Message d'erreur à afficher
        """
        print(f"ProjectExplorer ERREUR: {message}")
        # Si parent_window existe, afficher dans la barre de statut
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(f"❌ {message}", 5000)
        # Sinon, afficher dans une boîte de dialogue
        else:
            QMessageBox.critical(self, "Erreur", message)
            
    def show_warning(self, message):
        """
        Affiche un message d'avertissement.
        
        Args:
            message: Message d'avertissement à afficher
        """
        print(f"ProjectExplorer AVERTISSEMENT: {message}")
        # Si parent_window existe, afficher dans la barre de statut
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(f"⚠️ {message}", 3000)
        # Sinon, afficher dans une boîte de dialogue
        else:
            QMessageBox.warning(self, "Avertissement", message)
            
    def show_info(self, message):
        """
        Affiche un message d'information.
        
        Args:
            message: Message d'information à afficher
        """
        print(f"ProjectExplorer INFO: {message}")
        # Si parent_window existe, afficher dans la barre de statut
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(f"ℹ️ {message}", 2000)
        # Sinon, afficher dans une boîte de dialogue (optionnel)
        # else:
        #     QMessageBox.information(self, "Information", message)

# Pour tester le widget de manière isolée
if __name__ == '__main__':
    # Pour tests futurs, utiliser les fichiers de test appropriés
    # tests/gui/test_project_explorer.py
    pass