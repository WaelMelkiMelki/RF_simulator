# src/gui/widgets/antenna_library.py
"""
Bibliothèque d'antennes pour le RF Simulator 3D.
Permet de sélectionner, configurer et ajouter des antennes à la scène.
"""

import sys
import os
from pathlib import Path

# Ajout du chemin src si nécessaire
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton, QDialog,
    QDoubleSpinBox, QComboBox, QSpinBox, QDialogButtonBox,
    QMessageBox, QGroupBox, QTextEdit, QSplitter, QFrame,
    QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon

class AntennaLibrary(QWidget):
    """
    Widget de bibliothèque d'antennes.
    Permet de parcourir, sélectionner et configurer des antennes.
    """
    
    # Signaux émis par la bibliothèque
    antenna_selected = pyqtSignal(object)  # Émis quand une antenne est sélectionnée
    antenna_added = pyqtSignal(str, dict)  # Émis quand une antenne est ajoutée (type, config)
    
    def __init__(self, backend_adapter=None, parent=None):
        """
        Initialise la bibliothèque d'antennes.
        
        Args:
            backend_adapter: Adaptateur backend pour interaction
            parent: Widget parent Qt
        """
        super().__init__(parent)
        self.backend_adapter = backend_adapter
        self.parent_window = parent
        self.available_antennas = []
        
        self.init_ui()
        self.load_antenna_catalog()
        
    def init_ui(self):
        """Initialise l'interface utilisateur de la bibliothèque."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Titre
        title_label = QLabel("📡 Bibliothèque d'Antennes")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Créer un splitter horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- Panneau gauche : Liste des antennes ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Liste des antennes
        self.antenna_list = QListWidget()
        self.antenna_list.setIconSize(QSize(32, 32))
        self.antenna_list.itemSelectionChanged.connect(self.on_antenna_selection_changed)
        self.antenna_list.itemDoubleClicked.connect(self.on_antenna_double_clicked)
        left_layout.addWidget(self.antenna_list)
        
        splitter.addWidget(left_panel)
        
        # --- Panneau droit : Détails de l'antenne ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Groupe d'informations
        self.info_group = QGroupBox("📋 Informations")
        info_layout = QVBoxLayout(self.info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        info_layout.addWidget(self.info_text)
        
        right_layout.addWidget(self.info_group)
        
        # Groupe de configuration
        self.config_group = QGroupBox("⚙️ Configuration")
        config_layout = QFormLayout(self.config_group)
        
        # Position
        pos_layout = QHBoxLayout()
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-1000, 1000)
        self.pos_x_spin.setValue(0)
        self.pos_x_spin.setSingleStep(0.1)
        self.pos_x_spin.setSuffix(" m")
        pos_layout.addWidget(QLabel("X:"))
        pos_layout.addWidget(self.pos_x_spin)
        
        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-1000, 1000)
        self.pos_y_spin.setValue(0)
        self.pos_y_spin.setSingleStep(0.1)
        self.pos_y_spin.setSuffix(" m")
        pos_layout.addWidget(QLabel("Y:"))
        pos_layout.addWidget(self.pos_y_spin)
        
        self.pos_z_spin = QDoubleSpinBox()
        self.pos_z_spin.setRange(-1000, 1000)
        self.pos_z_spin.setValue(0)
        self.pos_z_spin.setSingleStep(0.1)
        self.pos_z_spin.setSuffix(" m")
        pos_layout.addWidget(QLabel("Z:"))
        pos_layout.addWidget(self.pos_z_spin)
        
        config_layout.addRow("Position:", pos_layout)
        
        # Fréquence
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["900 MHz", "1800 MHz", "2.4 GHz", "3.5 GHz", "5 GHz", "28 GHz"])
        config_layout.addRow("Fréquence:", self.frequency_combo)
        
        # Puissance
        self.power_spin = QSpinBox()
        self.power_spin.setRange(-100, 100)
        self.power_spin.setValue(20)
        self.power_spin.setSuffix(" dBm")
        config_layout.addRow("Puissance:", self.power_spin)
        
        # Gain
        self.gain_spin = QDoubleSpinBox()
        self.gain_spin.setRange(0, 50)
        self.gain_spin.setValue(5.0)
        self.gain_spin.setSingleStep(0.1)
        self.gain_spin.setSuffix(" dBi")
        config_layout.addRow("Gain:", self.gain_spin)
        
        right_layout.addWidget(self.config_group)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ Aperçu")
        self.preview_btn.clicked.connect(self.preview_antenna)
        self.preview_btn.setEnabled(False)
        button_layout.addWidget(self.preview_btn)
        
        self.add_btn = QPushButton("➕ Ajouter à la Scène")
        self.add_btn.clicked.connect(self.add_antenna_to_scene)
        self.add_btn.setEnabled(False)
        button_layout.addWidget(self.add_btn)
        
        button_layout.addStretch()
        
        right_layout.addLayout(button_layout)
        right_layout.addStretch()
        
        splitter.addWidget(right_panel)
        
        # Réglages du splitter
        splitter.setSizes([200, 400])  # Largeurs relatives
        
        layout.addWidget(splitter)
        
        # Zone de statut
        self.status_label = QLabel("Prêt")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)
        
    def load_antenna_catalog(self):
        """Charge le catalogue des antennes disponibles."""
        try:
            # Catalogue d'antennes prédéfinies
            self.available_antennas = [
                {
                    "id": "wifi_omni",
                    "name": "WiFi Omnidirectionnelle",
                    "type": "wifi",
                    "frequency_range": "2.4/5 GHz",
                    "gain": "2.5 dBi",
                    "pattern": "Omnidirectionnel",
                    "description": "Antenne WiFi standard avec rayonnement uniforme dans le plan horizontal."
                },
                {
                    "id": "5g_sector",
                    "name": "5G Secteur 65°",
                    "type": "5g",
                    "frequency_range": "3.5 GHz",
                    "gain": "15 dBi",
                    "pattern": "Secteur 65°",
                    "description": "Antenne 5G secteur pour stations de base, angle de 65°."
                },
                {
                    "id": "yagi_directional",
                    "name": "Yagi Directionnelle",
                    "type": "yagi",
                    "frequency_range": "2.4 GHz",
                    "gain": "12 dBi",
                    "pattern": "Directionnel",
                    "description": "Antenne Yagi haute directivité pour communications point-à-point."
                },
                {
                    "id": "lpda_broadband",
                    "name": "LPDA Large Bande",
                    "type": "lpda",
                    "frequency_range": "400-2000 MHz",
                    "gain": "8 dBi",
                    "pattern": "Large bande",
                    "description": "Antenne logarithmique périodique pour applications large bande."
                },
                {
                    "id": "patch_microstrip",
                    "name": "Patch Microbande",
                    "type": "patch",
                    "frequency_range": "5 GHz",
                    "gain": "6 dBi",
                    "pattern": "Secteur 90°",
                    "description": "Antenne patch compacte pour applications intégrées."
                }
            ]
            
            # Remplir la liste
            self.populate_antenna_list()
            
            self.status_label.setText(f"✅ {len(self.available_antennas)} antennes chargées")
            
        except Exception as e:
            error_msg = f"Erreur lors du chargement du catalogue: {e}"
            print(f"AntennaLibrary.load_antenna_catalog: {error_msg}")
            self.show_error(error_msg)
            
    def populate_antenna_list(self):
        """Remplit la liste avec les antennes disponibles."""
        try:
            self.antenna_list.clear()
            
            for antenna in self.available_antennas:
                item = QListWidgetItem(antenna["name"])
                item.setData(Qt.ItemDataRole.UserRole, antenna)
                
                # Définir une icône selon le type d'antenne (simplifié)
                # Dans une vraie application, vous auriez des icônes réelles
                antenna_type = antenna.get("type", "unknown")
                if antenna_type == "wifi":
                    item.setIcon(QIcon.fromTheme("network-wireless"))  # Icône système si disponible
                elif antenna_type == "5g":
                    item.setIcon(QIcon.fromTheme("network-cellular"))
                elif antenna_type == "yagi":
                    item.setIcon(QIcon.fromTheme("antenna"))  # Icône système si disponible
                else:
                    item.setIcon(QIcon.fromTheme("radio"))  # Icône par défaut
                    
                self.antenna_list.addItem(item)
                
            # Sélectionner le premier item par défaut
            if self.antenna_list.count() > 0:
                self.antenna_list.setCurrentRow(0)
                
        except Exception as e:
            error_msg = f"Erreur lors du remplissage de la liste: {e}"
            print(f"AntennaLibrary.populate_antenna_list: {error_msg}")
            self.show_error(error_msg)
            
    def on_antenna_selection_changed(self):
        """Gestionnaire appelé quand la sélection d'antenne change."""
        try:
            current_item = self.antenna_list.currentItem()
            if current_item:
                antenna_data = current_item.data(Qt.ItemDataRole.UserRole)
                self.display_antenna_info(antenna_data)
                self.enable_action_buttons(True)
            else:
                self.clear_antenna_info()
                self.enable_action_buttons(False)
                
        except Exception as e:
            error_msg = f"Erreur lors du changement de sélection: {e}"
            print(f"AntennaLibrary.on_antenna_selection_changed: {error_msg}")
            self.show_error(error_msg)
            
    def on_antenna_double_clicked(self, item):
        """Gestionnaire appelé quand une antenne est double-cliquée."""
        try:
            self.add_antenna_to_scene()
        except Exception as e:
            error_msg = f"Erreur lors du double-clic: {e}"
            print(f"AntennaLibrary.on_antenna_double_clicked: {error_msg}")
            self.show_error(error_msg)
            
    def display_antenna_info(self, antenna_data):
        """Affiche les informations détaillées d'une antenne."""
        try:
            if not antenna_data:
                self.clear_antenna_info()
                return
                
            # Construire le texte d'information
            info_text = f"<b>{antenna_data.get('name', 'Antenne Inconnue')}</b><br><br>"
            info_text += f"<b>Type:</b> {antenna_data.get('type', 'N/A')}<br>"
            info_text += f"<b>Plage de Fréquence:</b> {antenna_data.get('frequency_range', 'N/A')}<br>"
            info_text += f"<b>Gain:</b> {antenna_data.get('gain', 'N/A')}<br>"
            info_text += f"<b>Pattern:</b> {antenna_data.get('pattern', 'N/A')}<br><br>"
            info_text += f"<b>Description:</b><br>{antenna_data.get('description', 'Aucune description disponible.')}"
            
            self.info_text.setHtml(info_text)
            
            # Mettre à jour les valeurs par défaut de configuration
            self.set_default_config_values(antenna_data)
            
        except Exception as e:
            error_msg = f"Erreur lors de l'affichage des infos: {e}"
            print(f"AntennaLibrary.display_antenna_info: {error_msg}")
            self.show_error(error_msg)
            
    def clear_antenna_info(self):
        """Efface les informations d'antenne affichées."""
        self.info_text.clear()
        self.info_text.setHtml("<i>Sélectionnez une antenne pour voir ses détails.</i>")
        
    def set_default_config_values(self, antenna_data):
        """Définit les valeurs par défaut de configuration selon le type d'antenne."""
        try:
            antenna_type = antenna_data.get("type", "unknown")
            
            # Définir des valeurs par défaut selon le type
            if antenna_type == "wifi":
                self.frequency_combo.setCurrentText("2.4 GHz")
                self.power_spin.setValue(20)
                self.gain_spin.setValue(2.5)
            elif antenna_type == "5g":
                self.frequency_combo.setCurrentText("3.5 GHz")
                self.power_spin.setValue(30)
                self.gain_spin.setValue(15.0)
            elif antenna_type == "yagi":
                self.frequency_combo.setCurrentText("2.4 GHz")
                self.power_spin.setValue(25)
                self.gain_spin.setValue(12.0)
            elif antenna_type == "lpda":
                self.frequency_combo.setCurrentText("900 MHz")
                self.power_spin.setValue(15)
                self.gain_spin.setValue(8.0)
            elif antenna_type == "patch":
                self.frequency_combo.setCurrentText("5 GHz")
                self.power_spin.setValue(10)
                self.gain_spin.setValue(6.0)
            else:
                # Valeurs par défaut générales
                self.frequency_combo.setCurrentIndex(0)  # Premier item
                self.power_spin.setValue(20)
                self.gain_spin.setValue(5.0)
                
        except Exception as e:
            print(f"AntennaLibrary.set_default_config_values: Erreur: {e}")
            # En cas d'erreur, utiliser les valeurs par défaut existantes
            
    def enable_action_buttons(self, enabled):
        """Active ou désactive les boutons d'action."""
        self.preview_btn.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)
        
    def preview_antenna(self):
        """Affiche un aperçu de l'antenne sélectionnée."""
        try:
            current_item = self.antenna_list.currentItem()
            if not current_item:
                self.show_warning("Aucune antenne sélectionnée")
                return
                
            antenna_data = current_item.data(Qt.ItemDataRole.UserRole)
            antenna_name = antenna_data.get("name", "Antenne Inconnue")
            
            self.show_info(f"Aperçu de l'antenne '{antenna_name}' (fonctionnalité à implémenter)")
            
            # Émettre le signal de sélection
            self.antenna_selected.emit(antenna_data)
            
        except Exception as e:
            error_msg = f"Erreur lors de l'aperçu: {e}"
            print(f"AntennaLibrary.preview_antenna: {error_msg}")
            self.show_error(error_msg)
            
    def add_antenna_to_scene(self):
        """Ajoute l'antenne sélectionnée à la scène avec la configuration actuelle."""
        try:
            current_item = self.antenna_list.currentItem()
            if not current_item:
                self.show_warning("Veuillez sélectionner une antenne")
                return
                
            antenna_data = current_item.data(Qt.ItemDataRole.UserRole)
            
            # Créer la configuration à partir des widgets
            # Générer un nom unique pour chaque antenne
            if not hasattr(self, 'antenna_counter'):
                self.antenna_counter = 1
            else:
                self.antenna_counter += 1
            config = {
                "name": f"{antenna_data.get('name', 'Nouvelle Antenne')} #{self.antenna_counter}",
                "position": [
                    self.pos_x_spin.value(),
                    self.pos_y_spin.value(),
                    self.pos_z_spin.value()
                ],
                "frequency": self.frequency_combo.currentText(),
                "power_dbm": self.power_spin.value(),
                "gain": self.gain_spin.value(),
                "type": antenna_data.get("type", "unknown")
            }
            
            # === AJOUT POUR DIAGNOSTIC ===
            print(f"DEBUG AntennaLibrary: Configuration envoyée au backend: {config}")
            print(f"DEBUG AntennaLibrary: Position lue depuis les spinboxes: {config['position']}")
            # =============================
            
            # Si backend disponible, utiliser le backend
            if self.backend_adapter:
                try:
                    # Ajouter via le backend
                    self.backend_adapter.add_antenna(antenna_data.get("type", "unknown"), config)
                    self.show_info(f"Antenne '{config['name']}' ajoutée à la scène")
                    
                    # Émettre le signal
                    self.antenna_added.emit(antenna_data.get("type", "unknown"), config)
                    
                except Exception as backend_error:
                    # En cas d'erreur backend, ajouter directement
                    self.show_warning(f"Backend indisponible, ajout direct: {backend_error}")
                    self.antenna_added.emit(antenna_data.get("type", "unknown"), config)
            else:
                # Ajouter directement si pas de backend
                self.show_info(f"Antenne '{config['name']}' prête à être ajoutée")
                self.antenna_added.emit(antenna_data.get("type", "unknown"), config)
                
        except Exception as e:
            error_msg = f"Erreur lors de l'ajout de l'antenne: {e}"
            print(f"AntennaLibrary.add_antenna_to_scene: {error_msg}")
            self.show_error(error_msg)
            
    def refresh_library(self):
        """Actualise la bibliothèque d'antennes."""
        try:
            self.load_antenna_catalog()
            self.status_label.setText("🔄 Bibliothèque actualisée")
        except Exception as e:
            error_msg = f"Erreur lors de l'actualisation: {e}"
            print(f"AntennaLibrary.refresh_library: {error_msg}")
            self.show_error(error_msg)
            
    def search_antennas(self, search_term):
        """
        Recherche des antennes par terme.
        
        Args:
            search_term: Terme de recherche (nom, type, fréquence)
        """
        try:
            # Pour l'instant, filtrer la liste existante
            # Dans une vraie application, cela pourrait interroger une base de données
            search_term = search_term.lower()
            
            for i in range(self.antenna_list.count()):
                item = self.antenna_list.item(i)
                antenna_data = item.data(Qt.ItemDataRole.UserRole)
                
                # Vérifier si le terme de recherche correspond à un champ
                match = (
                    search_term in antenna_data.get("name", "").lower() or
                    search_term in antenna_data.get("type", "").lower() or
                    search_term in antenna_data.get("frequency_range", "").lower()
                )
                
                # Afficher ou masquer l'item
                item.setHidden(not match)
                
            self.status_label.setText(f"Recherche effectuée pour '{search_term}'")
            
        except Exception as e:
            error_msg = f"Erreur lors de la recherche: {e}"
            print(f"AntennaLibrary.search_antennas: {error_msg}")
            self.show_error(error_msg)
            
    def show_error(self, message):
        """
        Affiche un message d'erreur.
        
        Args:
            message: Message d'erreur à afficher
        """
        print(f"AntennaLibrary ERREUR: {message}")
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        # Afficher dans la barre de statut de la fenêtre principale si disponible
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(f"❌ {message}", 5000)
                
    def show_warning(self, message):
        """
        Affiche un message d'avertissement.
        
        Args:
            message: Message d'avertissement à afficher
        """
        print(f"AntennaLibrary AVERTISSEMENT: {message}")
        self.status_label.setText(f"⚠️ {message}")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        # Afficher dans la barre de statut de la fenêtre principale si disponible
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(f"⚠️ {message}", 3000)
                
    def show_info(self, message):
        """
        Affiche un message d'information.
        
        Args:
            message: Message d'information à afficher
        """
        print(f"AntennaLibrary INFO: {message}")
        self.status_label.setText(f"ℹ️ {message}")
        self.status_label.setStyleSheet("color: blue;")
        
        # Afficher dans la barre de statut de la fenêtre principale si disponible
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(f"ℹ️ {message}", 2000)

# Backend factice pour les tests
class FakeBackend:
    """Backend factice pour tester l'interface sans vraie base de données."""
    def get_available_antennas(self):
        return [
            {"name": "WiFi Omni", "type": "wifi"},
            {"name": "5G Sector", "type": "5g"}
        ]
        
    def add_antenna(self, antenna_type, config):
        print(f"FakeBackend.add_antenna: type={antenna_type}, config={config}")

# Pour tester le widget de manière isolée
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Créer un backend factice pour le test
    class FakeBackend:
        def get_available_antennas(self):
            return [
                {"name": "WiFi Omni", "type": "wifi"},
                {"name": "5G Sector", "type": "5g"}
            ]
            
        def add_antenna(self, antenna_type, config):
            print(f"FakeBackend.add_antenna: type={antenna_type}, config={config}")
    
    # Créer et afficher la bibliothèque
    library = AntennaLibrary(backend_adapter=FakeBackend())
    library.show()
    
    sys.exit(app.exec())