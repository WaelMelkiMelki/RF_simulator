# src/gui/dialogs/scene_objects_dialog.py
"""
Dialogue pour visualiser et sélectionner les objets d'une scène importée.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QListWidgetItem, QPushButton, 
                             QLabel, QSplitter, QGroupBox, QCheckBox,
                             QSpinBox, QSlider, QColorDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import numpy as np

class SceneObjectsDialog(QDialog):
    """Dialogue pour explorer et assigner les objets de la scène."""
    
    object_selected = pyqtSignal(str)  # Signal émis quand un objet est sélectionné
    object_highlighted = pyqtSignal(str, bool)  # Signal pour mettre en surbrillance
    material_assigned = pyqtSignal(str, dict)  # Signal pour assigner un matériau
    
    @staticmethod
    def get_friendly_name(technical_name):
        """Convertit un nom technique en nom convivial."""
        if not technical_name or not isinstance(technical_name, str):
            return "Objet Inconnu"
        
        # Mappings spécifiques pour les objets courants
        object_mappings = {
            "Block_0/Block_0/Block_0/Block_0/Block_0": "Bâtiment 1",
            "Block_0/Block_0/Block_1/Block_0/Block_0": "Bâtiment 2", 
            "Block_0/Block_0/Block_2/Block_0/Block_0": "Bâtiment 3",
            "Block_0/Block_0/Block_3/Block_0/Block_0": "Bâtiment 4",
            "Block_0/Block_0/Block_4/Block_0/Block_0": "Bâtiment 5"
        }
        
        # Si on a un mapping direct, l'utiliser
        if technical_name in object_mappings:
            return object_mappings[technical_name]
        
        # Sinon, essayer d'extraire un nom plus lisible
        # Chercher des patterns comme Block_X pour créer "Objet X"
        if "Block_" in technical_name:
            # Extraire le dernier numéro de Block_X
            parts = technical_name.split("/")
            for part in reversed(parts):
                if part.startswith("Block_") and len(part) > 6:
                    try:
                        num = int(part.split("_")[1]) + 1  # +1 pour commencer à 1 au lieu de 0
                        return f"Objet {num}"
                    except:
                        pass
        
        # Fallback : utiliser le nom technique mais raccourci
        if len(technical_name) > 20:
            return f"Objet ({technical_name[:15]}...)"
        
        return technical_name
    
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.selected_object = None
        self.highlighted_objects = set()
        self.selected_color = "#FF6464"  # Couleur par défaut
        
        self.setWindowTitle("Objets de la scène - Navigation et assignation")
        self.setModal(False)  # Dialogue non-modal pour permettre l'interaction avec la 3D
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_scene_objects()
        
    def setup_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        
        # Splitter principal horizontal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # === PANNEAU GAUCHE: Liste des objets ===
        left_panel = QGroupBox("Objets de la scène")
        left_layout = QVBoxLayout(left_panel)
        
        # Liste des objets
        self.objects_list = QListWidget()
        self.objects_list.itemClicked.connect(self.on_object_clicked)
        left_layout.addWidget(self.objects_list)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        self.clear_highlight_btn = QPushButton("🔄 Réinitialiser couleurs")
        self.clear_highlight_btn.clicked.connect(self.reset_all_colors)
        buttons_layout.addWidget(self.clear_highlight_btn)
        
        left_layout.addLayout(buttons_layout)
        main_splitter.addWidget(left_panel)
        
        # === PANNEAU DROIT: Propriétés et assignation ===
        right_panel = QGroupBox("Propriétés et assignation")
        right_layout = QVBoxLayout(right_panel)
        
        # Informations sur l'objet sélectionné
        self.object_info_label = QLabel("Sélectionnez un objet pour voir ses propriétés")
        self.object_info_label.setWordWrap(True)
        right_layout.addWidget(self.object_info_label)
        
        # --- Section assignation de matériau ---
        material_group = QGroupBox("Assignation de matériau")
        material_layout = QVBoxLayout(material_group)
        
        # Sélection de couleur pour l'objet
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Couleur de visualisation:"))
        self.color_btn = QPushButton("Choisir couleur")
        self.color_btn.clicked.connect(self.choose_color)
        self.color_btn.setEnabled(False)
        color_layout.addWidget(self.color_btn)
        material_layout.addLayout(color_layout)
        
        # Propriétés RF du matériau
        # Permittivité relative
        perm_layout = QHBoxLayout()
        perm_layout.addWidget(QLabel("Permittivité relative:"))
        self.permittivity_spin = QSpinBox()
        self.permittivity_spin.setRange(1, 100)
        self.permittivity_spin.setValue(1)
        self.permittivity_spin.setEnabled(False)
        perm_layout.addWidget(self.permittivity_spin)
        material_layout.addLayout(perm_layout)
        
        # Conductivité
        cond_layout = QHBoxLayout()
        cond_layout.addWidget(QLabel("Conductivité (S/m):"))
        self.conductivity_spin = QSpinBox()
        self.conductivity_spin.setRange(0, 1000)
        self.conductivity_spin.setValue(0)
        self.conductivity_spin.setEnabled(False)
        cond_layout.addWidget(self.conductivity_spin)
        material_layout.addLayout(cond_layout)
        
        # Atténuation
        atten_layout = QHBoxLayout()
        atten_layout.addWidget(QLabel("Atténuation (dB/m):"))
        self.attenuation_spin = QSpinBox()
        self.attenuation_spin.setRange(0, 100)
        self.attenuation_spin.setValue(0)
        self.attenuation_spin.setEnabled(False)
        atten_layout.addWidget(self.attenuation_spin)
        material_layout.addLayout(atten_layout)
        
        # Bouton d'assignation
        self.assign_btn = QPushButton("✅ Assigner le matériau")
        self.assign_btn.clicked.connect(self.assign_material)
        self.assign_btn.setEnabled(False)
        material_layout.addWidget(self.assign_btn)
        
        right_layout.addWidget(material_group)
        
        # --- Section outils de navigation ---
        nav_group = QGroupBox("Outils de navigation")
        nav_layout = QVBoxLayout(nav_group)
        
        # Checkbox pour auto-centrage
        self.auto_center_check = QCheckBox("Centrer automatiquement sur l'objet sélectionné")
        self.auto_center_check.setChecked(True)
        nav_layout.addWidget(self.auto_center_check)
        
        # Intensité de la surbrillance
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("Intensité surbrillance:"))
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(50, 255)
        self.intensity_slider.setValue(150)
        intensity_layout.addWidget(self.intensity_slider)
        nav_layout.addLayout(intensity_layout)
        
        right_layout.addWidget(nav_group)
        
        right_layout.addStretch()  # Pousser le contenu vers le haut
        main_splitter.addWidget(right_panel)
        
        # Proportions du splitter
        main_splitter.setSizes([400, 400])
        
        # Boutons de fermeture
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        
        layout.addLayout(close_layout)
        
    def load_scene_objects(self):
        """Charge la liste des objets de la scène."""
        if not self.scene:
            return
            
        try:
            # Obtenir les noms des mesh de la scène
            mesh_names = self.scene.get_mesh_names() if hasattr(self.scene, 'get_mesh_names') else []
            
            self.objects_list.clear()
            
            for i, mesh_name in enumerate(mesh_names):
                friendly_name = self.get_friendly_name(mesh_name)
                item = QListWidgetItem(f"📦 {friendly_name}")
                item.setData(Qt.ItemDataRole.UserRole, mesh_name)  # Garder le nom technique dans les données
                
                # Ajouter des informations sur l'objet
                try:
                    # Obtenir le mesh pour calculer des statistiques
                    mesh = self.scene.get_pyvista_mesh()
                    if mesh and hasattr(mesh, 'n_cells'):
                        item.setToolTip(f"Objet: {mesh_name}\nNombre de cellules: {mesh.n_cells}")
                except:
                    item.setToolTip(f"Objet: {mesh_name}")
                
                self.objects_list.addItem(item)
                
            if len(mesh_names) == 0:
                # Ajouter un item par défaut si pas d'objets nommés
                item = QListWidgetItem("📦 Scène principale")
                item.setData(Qt.ItemDataRole.UserRole, "main_scene")
                item.setToolTip("Scène principale")
                self.objects_list.addItem(item)
                
        except Exception as e:
            print(f"Erreur lors du chargement des objets: {e}")
            # Fallback: ajouter un objet générique
            item = QListWidgetItem("📦 Scène (objets non nommés)")
            item.setData(Qt.ItemDataRole.UserRole, "unnamed_objects")
            self.objects_list.addItem(item)
    
    def on_object_clicked(self, item):
        """Appelé quand un objet est cliqué."""
        object_name = item.data(Qt.ItemDataRole.UserRole)
        self.selected_object = object_name
        
        # Mettre à jour l'interface
        self.color_btn.setEnabled(True)
        self.permittivity_spin.setEnabled(True)
        self.conductivity_spin.setEnabled(True)
        self.attenuation_spin.setEnabled(True)
        self.assign_btn.setEnabled(True)
        
        # Mettre à jour les informations
        self.update_object_info(object_name)
        
        # Émettre le signal de sélection
        self.object_selected.emit(object_name)
        
    def update_object_info(self, object_name):
        """Met à jour les informations sur l'objet sélectionné."""
        friendly_name = self.get_friendly_name(object_name)
        info_text = f"<b>Objet sélectionné:</b> {friendly_name}<br>"
        info_text += f"<small><i>Nom technique: {object_name}</i></small><br><br>"
        
        try:
            # Essayer d'obtenir des informations sur le mesh
            if self.scene and hasattr(self.scene, 'get_pyvista_mesh'):
                mesh = self.scene.get_pyvista_mesh()
                if mesh:
                    bounds = mesh.bounds
                    center = mesh.center
                    info_text += f"<b>Centre:</b> ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})<br>"
                    info_text += f"<b>Dimensions:</b><br>"
                    info_text += f"  X: {bounds[0]:.1f} → {bounds[1]:.1f}<br>"
                    info_text += f"  Y: {bounds[2]:.1f} → {bounds[3]:.1f}<br>"
                    info_text += f"  Z: {bounds[4]:.1f} → {bounds[5]:.1f}<br>"
                    info_text += f"<b>Cellules:</b> {mesh.n_cells}<br>"
                    info_text += f"<b>Points:</b> {mesh.n_points}<br>"
                    
        except Exception as e:
            info_text += f"<i>Informations détaillées non disponibles</i><br>"
            
        self.object_info_label.setText(info_text)
        
    def clear_all_highlights(self):
        """Efface toutes les surbrillances."""
        for obj_name in list(self.highlighted_objects):
            self.object_highlighted.emit(obj_name, False)
        self.highlighted_objects.clear()
        
    def reset_all_colors(self):
        """Remet tous les objets à leur couleur par défaut (gris)."""
        if not self.scene:
            return
            
        # Obtenir la liste des objets
        object_names = []
        if hasattr(self.scene, 'get_mesh_names'):
            object_names = self.scene.get_mesh_names()
        elif hasattr(self.scene, 'meshes') and self.scene.meshes:
            object_names = list(self.scene.meshes.keys())
            
        # Émettre un signal pour réinitialiser chaque objet à sa couleur par défaut
        for obj_name in object_names:
            default_material = {
                'name': f'Default_{obj_name}',
                'permittivity': 1,
                'conductivity': 0,
                'attenuation': 0,
                'color': '#808080'  # Gris par défaut
            }
            self.material_assigned.emit(obj_name, default_material)
            
        # Effacer aussi les surbrillances
        self.clear_all_highlights()
        
        # Message de confirmation
        if hasattr(self, 'object_info_label'):
            self.object_info_label.setText("<i>Toutes les couleurs ont été réinitialisées en gris</i>")
        
    def choose_color(self):
        """Ouvre un dialogue de sélection de couleur."""
        color = QColorDialog.getColor(QColor(255, 100, 100), self, "Choisir la couleur de l'objet")
        if color.isValid():
            self.selected_color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {color.name()}")
            
    def assign_material(self):
        """Assigne le matériau configuré à l'objet sélectionné."""
        if not self.selected_object:
            return
            
        # Construire le dictionnaire des propriétés du matériau
        material = {
            'name': f"Material_{self.selected_object}",
            'permittivity': self.permittivity_spin.value(),
            'conductivity': self.conductivity_spin.value(),
            'attenuation': self.attenuation_spin.value(),
            'color': self.selected_color
        }
        
        # Émettre le signal d'assignation
        self.material_assigned.emit(self.selected_object, material)
        
        # Notification visuelle
        original_text = self.assign_btn.text()
        self.assign_btn.setText("✅ Matériau assigné!")
        self.assign_btn.setEnabled(False)
        
        # Restaurer après 2 secondes
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: [
            self.assign_btn.setText(original_text),
            self.assign_btn.setEnabled(True)
        ])
