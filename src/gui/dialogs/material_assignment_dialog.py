# src/gui/dialogs/material_assignment_dialog.py
"""
Dialogue pour associer des matériaux aux meshes d'une scène 3D.
S'affiche après le chargement d'une scène GLTF.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QPushButton, QLabel, QHeaderView, QAbstractItemView,
    QApplication, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.domain.scene import Scene3D
# Nous importerons les matériaux disponibles via le constructeur

logger = logging.getLogger(__name__)

class MaterialAssignmentDialog(QDialog):
    """
    Dialogue modale pour associer des matériaux aux meshes d'une scène GLTF.
    """
    # Signal émis lorsque l'utilisateur confirme les changements
    materials_assigned = pyqtSignal(dict) # {mesh_name: material_name}
    # Ajoutez ce signal
    mesh_selected_from_dialog = pyqtSignal(int)

    def __init__(self, scene: Scene3D, available_materials: list, parent=None):
        """
        Initialise le dialogue.

        Args:
            scene (Scene3D): La scène contenant les meshes.
            available_materials (list): Liste des noms de matériaux disponibles.
            parent (QWidget, optional): Widget parent. Defaults to None.
        """
        super().__init__(parent)
        self.scene = scene
        self.available_materials = available_materials
        self.mesh_names = self.scene.get_mesh_names()
        
        # Stocker les associations temporaires avant validation
        self.temp_assignments = self.scene.mesh_material_mapping.copy()
        
        self.setWindowTitle("Attribution des Matériaux")
        self.setModal(True)
        self.setMinimumSize(600, 400) # Taille raisonnable
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instruction_label = QLabel("Associez un matériau à chaque objet (mesh) de la scène :")
        layout.addWidget(instruction_label)
        
        # Table pour lister les meshes et choisir les matériaux
        self.table = QTableWidget(0, 2, self) # 0 lignes, 2 colonnes
        self.table.setHorizontalHeaderLabels(["Nom de l'Objet (Mesh)", "Matériau"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Rendre les cellules non éditables directement
        
        layout.addWidget(self.table)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Annuler")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Remplir la table
        self.populate_table()

        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)

    def populate_table(self):
        """Remplit la table avec les meshes et les combobox de matériaux."""
        self.table.setRowCount(len(self.mesh_names))
        
        for row, mesh_name in enumerate(self.mesh_names):
            # Colonne 1 : Nom du mesh
            mesh_item = QTableWidgetItem(mesh_name)
            mesh_item.setFlags(mesh_item.flags() & ~Qt.ItemFlag.ItemIsEditable) # Non éditable
            self.table.setItem(row, 0, mesh_item)
            
            # Colonne 2 : ComboBox pour le matériau
            combo = QComboBox()
            combo.addItems(self.available_materials)
            
            # Sélectionner le matériau actuellement associé
            current_material = self.temp_assignments.get(mesh_name, "default")
            if current_material in self.available_materials:
                index = self.available_materials.index(current_material)
                combo.setCurrentIndex(index)
            else:
                # Si le matériau actuel n'est pas dans la liste, sélectionner "default" ou le premier
                default_index = self.available_materials.index("default") if "default" in self.available_materials else 0
                combo.setCurrentIndex(default_index)
                # Mettre à jour temp_assignments
                self.temp_assignments[mesh_name] = self.available_materials[default_index]
            
            # Connecter le changement de sélection à une méthode
            # Utilisation d'une lambda avec valeur par défaut pour capturer `mesh_name`
            combo.currentTextChanged.connect(
                lambda text, name=mesh_name: self.on_material_changed(name, text)
            )
            
            # Ajouter le combo à la cellule
            self.table.setCellWidget(row, 1, combo)
            
        logger.debug(f"MaterialAssignmentDialog: Table remplie avec {len(self.mesh_names)} meshes.")

    def on_material_changed(self, mesh_name: str, material_name: str):
        """
        Callback appelé lorsque l'utilisateur change la sélection d'un matériau.
        
        Args:
            mesh_name (str): Nom du mesh concerné.
            material_name (str): Nouveau nom de matériau sélectionné.
        """
        logger.debug(f"MaterialAssignmentDialog: Changement de matériau pour '{mesh_name}' -> '{material_name}'")
        self.temp_assignments[mesh_name] = material_name

    def accept(self):
        """
        Surcharge de la méthode accept pour émettre le signal avant de fermer.
        """
        logger.info("MaterialAssignmentDialog: Validation des associations de matériaux.")
        # Émettre le signal avec les nouvelles associations
        self.materials_assigned.emit(self.temp_assignments.copy())
        super().accept() # Fermer le dialogue

    def select_mesh_by_index(self, index):
        """Sélectionne un mesh dans la table par index."""
        if index < self.table.rowCount():
            self.table.selectRow(index)
            # Optionnel : faire défiler jusqu'à la ligne
            self.table.scrollToItem(self.table.item(index, 0))

    def on_table_selection_changed(self):
        """Émet un signal lorsque la sélection de la table change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            index = selected_rows[0].row()
            self.mesh_selected_from_dialog.emit(index)


    def on_mesh_hovered(self, mesh_name):
        """Callback lorsqu'un mesh est survolé dans la visualisation."""
        # Trouver la ligne correspondante dans la table
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == mesh_name:
                # Surligner la ligne
                self.table.selectRow(row)
                break

    def select_mesh_by_name(self, mesh_name):
        """Sélectionne un mesh dans la table par son nom."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == mesh_name:
                self.table.selectRow(row)
                self.table.scrollToItem(item)
                break
