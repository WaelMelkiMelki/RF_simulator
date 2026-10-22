from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QLabel,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QCheckBox,
    QTabWidget,
    QTextEdit,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class PropertiesPanel(QWidget):
    def on_voxel_size_changed(self, value):
        """Gère le changement de la taille du voxel."""
        assert hasattr(
            self, "simulation_config"
        ), "Erreur: cette méthode doit être une méthode de classe"
        self.simulation_config["voxel_size"] = value
        self.simulation_config_changed.emit(self.simulation_config)
        if hasattr(self, "status_label"):
            self.status_label.setText(f"Taille du voxel mise à jour: {value}m")
        if __debug__:
            print(f"PropertiesPanel.on_voxel_size_changed: {value}")

    def _safe_set_combobox_text(self, combo_box, text):
        """Définit le texte d'un QComboBox en toute sécurité."""
        if combo_box and text:
            try:
                combo_box.setCurrentText(text)
            except RuntimeError as re:
                if "wrapped C/C++ object" in str(re) and "has been deleted" in str(re):
                    print(
                        f"PropertiesPanel._safe_set_combobox_text: Widget {combo_box.objectName() if hasattr(combo_box, 'objectName') else 'Unknown'} seems to be deleted. Skipping update."
                    )
                else:
                    raise

    def _safe_set_spinbox_value(self, spin_box, value):
        """Définit la valeur d'un QSpinBox/QDoubleSpinBox en toute sécurité."""
        if spin_box is None or value is None:
            return
        try:
            from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox
            if isinstance(spin_box, QSpinBox):
                # Pour QSpinBox, utiliser un entier strictement
                spin_box.setValue(int(float(value)))
            elif isinstance(spin_box, QDoubleSpinBox):
                # Pour QDoubleSpinBox, utiliser un float
                spin_box.setValue(float(value))
            else:
                print(f"PropertiesPanel._safe_set_spinbox_value: Type de spinbox inconnu: {type(spin_box)}")
        except RuntimeError as re:
            if "wrapped C/C++ object" in str(re) and "has been deleted" in str(re):
                print(f"PropertiesPanel._safe_set_spinbox_value: Widget {spin_box.objectName() if hasattr(spin_box, 'objectName') else 'Unknown'} seems to be deleted. Skipping update.")
            else:
                raise
        except (ValueError, TypeError) as e:
            print(f"PropertiesPanel._safe_set_spinbox_value: Invalid value '{value}' for spinbox. Error: {e}")
    def validate_config_types(self, config):
        """Valide et normalise les types de données dans la configuration."""
        expected_types = {
            'model': str,
            'resolution': (int, float),
            'frequency': str,
            'reflections': (int, float),
            'diffraction': bool,
            'backend': str,
            'parallel': bool
        }
        for key, expected_type in expected_types.items():
            if key in config and not isinstance(config[key], expected_type):
                print(f"WARNING: Type incorrect pour {key}. Attendu: {expected_type}, Reçu: {type(config[key])}")
                # Optionnel : conversion automatique si possible
                if isinstance(expected_type, tuple) and float in expected_type:
                    try:
                        config[key] = float(config[key])
                    except (TypeError, ValueError):
                        pass
                        pass

    """
    Panneau de propriétés pour configurer les paramètres de simulation.
    Émet des signaux lorsque les paramètres sont modifiés.
    """
    # Définition des signaux (à connecter dans MainWindow ou BackendAdapter)
    simulation_config_changed = pyqtSignal(
        dict
    )  # Émis lorsque la config globale change
    antenna_selected = pyqtSignal(object)  # Émis lorsqu'une antenne est sélectionnée
    antenna_config_changed = pyqtSignal(
        dict
    )  # Émis lorsque la config d'une antenne change

    def __init__(self, backend_adapter=None, parent=None):
        super().__init__(parent)
        self.backend_adapter = backend_adapter
        self.parent_window = parent
        self.current_antenna = None
        self.init_ui()
        self.populate_initial_config()

    def init_ui(self):
        """Initialise l'interface utilisateur du panneau de propriétés."""
        try:
            # Layout principal
            layout = QVBoxLayout(self)
            layout.setContentsMargins(5, 5, 5, 5)

            # Titre
            title_label = QLabel("PropertyParams")
            title_font = QFont()
            title_font.setBold(True)
            title_font.setPointSize(12)
            title_label.setFont(title_font)
            layout.addWidget(title_label)

            # Groupe de configuration globale
            self.sim_group = QGroupBox("Configuration Globale")
            sim_group_layout = QFormLayout(self.sim_group)

            # Modèle de propagation
            self.model_combo = QComboBox()
            self.model_combo.addItems(["Free Space", "Ray Tracing"])
            sim_group_layout.addRow("Modèle de Propagation:", self.model_combo)

            # Résolution de la grille
            self.resolution_spin = QDoubleSpinBox()
            self.resolution_spin.setRange(0.1, 10.0)
            self.resolution_spin.setSingleStep(0.1)
            self.resolution_spin.setValue(1.0)
            self.resolution_spin.setSuffix(" m")
            sim_group_layout.addRow("Résolution de Grille:", self.resolution_spin)

            # Voxel Size
            self.voxel_size_spin = QDoubleSpinBox()
            self.voxel_size_spin.setRange(0.01, 100.0)
            self.voxel_size_spin.setSingleStep(0.01)
            self.voxel_size_spin.setDecimals(2)
            self.voxel_size_spin.setValue(1.0)
            self.voxel_size_spin.setSuffix(" m")
            self.voxel_size_spin.valueChanged.connect(self.on_voxel_size_changed)
            sim_group_layout.addRow("Voxel Size:", self.voxel_size_spin)

            # Fréquence
            self.frequency_combo = QComboBox()
            self.frequency_combo.addItems(["2.4 GHz", "5 GHz", "3.5 GHz", "28 GHz"])
            sim_group_layout.addRow("Fréquence par défaut:", self.frequency_combo)

            # Réflexions
            self.reflections_spin = QSpinBox()
            self.reflections_spin.setRange(0, 10)
            self.reflections_spin.setValue(3)
            sim_group_layout.addRow("Réflexions:", self.reflections_spin)

            # Diffraction
            self.diffractions_check = QCheckBox("Diffraction")
            self.diffractions_check.setChecked(True)
            sim_group_layout.addRow("Diffraction:", self.diffractions_check)

            # Ajouter le groupe à un layout
            sim_layout = QVBoxLayout()
            sim_layout.addWidget(self.sim_group)
            layout.addLayout(sim_layout)

            # Créer les onglets
            self.tab_widget = QTabWidget()
            layout.addWidget(self.tab_widget)
            # CRITIQUE : Appeler les méthodes de création d'onglets
            self.create_simulation_tab()
            self.create_advanced_tab()

            # Connexions des signaux
            self.resolution_spin.valueChanged.connect(self.apply_simulation_config)
            self.voxel_size_spin.valueChanged.connect(self.update_voxel_size_related_widgets)
            self.voxel_size_spin.valueChanged.connect(self.apply_simulation_config)
            self.update_voxel_size_related_widgets()

            # Label de statut
            self.status_label = QLabel("Configuration prête")
            self.status_label.setStyleSheet("color: blue;")
            layout.addWidget(self.status_label)

        except Exception as e:
            print(f"Error initializing UI: {e}")
            import traceback
            traceback.print_exc()

    def update_config(self, key, value):
        """Mise à jour de la configuration avec les valeurs des widgets."""
        if key == 'reflections':
            self.simulation_config[key] = value
            self.simulation_config_changed.emit(self.simulation_config)
        # ...existing code...

    def update_voxel_size_related_widgets(self, value=None):
        """Active/Désactive les widgets resolution/height_levels en fonction de voxel_size."""
        # Vérifier que les widgets nécessaires existent
        if not hasattr(self, 'resolution_spin'):
            return

        voxel_size = self.voxel_size_spin.value()
        is_voxel_size_active = voxel_size > 0.01

        # Désactiver la résolution si voxel_size actif
        self.resolution_spin.setEnabled(not is_voxel_size_active)

        # Mettre à jour le statut si nécessaire
        if hasattr(self, 'status_label') and is_voxel_size_active:
            self.status_label.setText("⚠️ Résolution désactivée (utilisation de voxel_size)")

    def create_simulation_tab(self):
        """Crée l'onglet Simulation (Antenne) et l'ajoute au tab_widget."""
        antenna_widget = QWidget()
        antenna_layout = QVBoxLayout(antenna_widget)

        # CRITIQUE : Créer le label AVANT de l'utiliser
        self.antenna_info_label = QLabel("Sélectionnez une antenne dans la scène pour modifier ses propriétés.")
        self.antenna_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.antenna_info_label.setStyleSheet("color: gray; font-style: italic;")
        antenna_layout.addWidget(self.antenna_info_label)

        # Groupe des propriétés de l'antenne
        self.antenna_group = QGroupBox("Propriétés de l'Antenne")
        self.antenna_group.setEnabled(False)
        antenna_props_layout = QFormLayout(self.antenna_group)

        # Nom
        self.antenna_name_edit = QLineEdit()
        antenna_props_layout.addRow("Nom:", self.antenna_name_edit)

        # Type
        self.antenna_type_label = QLabel("N/A")
        antenna_props_layout.addRow("Type:", self.antenna_type_label)

        # SUPPRESSION TOTALE DU CURSEUR DE POSITION
        antenna_props_layout.addRow("Position (m):", QLabel("Position masquée"))

        # Fréquence
        self.antenna_freq_combo = QComboBox()
        self.antenna_freq_combo.addItems(["2.4 GHz", "5 GHz", "3.5 GHz", "28 GHz"])
        antenna_props_layout.addRow("Fréquence:", self.antenna_freq_combo)

        # Puissance
        self.antenna_power_spin = QDoubleSpinBox()
        self.antenna_power_spin.setRange(-100, 100)
        self.antenna_power_spin.setSingleStep(1)
        self.antenna_power_spin.setValue(20.0)
        self.antenna_power_spin.setSuffix(" dBm")
        antenna_props_layout.addRow("Puissance:", self.antenna_power_spin)

        # Gain
        self.antenna_gain_spin = QDoubleSpinBox()
        self.antenna_gain_spin.setRange(0, 50)
        self.antenna_gain_spin.setSingleStep(0.1)
        self.antenna_gain_spin.setValue(5.0)
        self.antenna_gain_spin.setSuffix(" dBi")
        antenna_props_layout.addRow("Gain:", self.antenna_gain_spin)
        
        # Titre du curseur d'opacité des points
        self.point_opacity_title = QLabel("Opacité des points")
        self.point_opacity_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        antenna_props_layout.addRow(self.point_opacity_title)

        antenna_layout.addWidget(self.antenna_group)

        # Boutons d'action pour l'antenne
        antenna_button_layout = QHBoxLayout()
        self.apply_antenna_btn = QPushButton("✅ Appliquer")
        self.apply_antenna_btn.clicked.connect(self.apply_antenna_config)
        self.apply_antenna_btn.setEnabled(False)
        antenna_button_layout.addWidget(self.apply_antenna_btn)

        self.reset_antenna_btn = QPushButton("🔄 Réinitialiser")
        self.reset_antenna_btn.clicked.connect(self.reset_antenna_config)
        self.reset_antenna_btn.setEnabled(False)
        antenna_button_layout.addWidget(self.reset_antenna_btn)

        antenna_button_layout.addStretch()
        antenna_layout.addLayout(antenna_button_layout)
        antenna_layout.addStretch()

        self.tab_widget.addTab(antenna_widget, "📡 Antenne")

    def create_advanced_tab(self):
        """Crée l'onglet de configuration avancée."""
        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout(advanced_widget)

        # Groupe de calculs
        calc_group = QGroupBox("Calculs Avancés")
        calc_layout = QFormLayout(calc_group)

        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["optimized", "default"])
        calc_layout.addRow("Backend de Calcul:", self.backend_combo)

        self.parallel_check = QCheckBox("Calculs Parallèles")
        self.parallel_check.setChecked(True)
        calc_layout.addRow("Parallélisme:", self.parallel_check)

        self.precision_combo = QComboBox()
        self.precision_combo.addItems(["simple", "double"])
        calc_layout.addRow("Précision:", self.precision_combo)

        advanced_layout.addWidget(calc_group)

        # Groupe de cache
        cache_group = QGroupBox("Gestion du Cache")
        cache_layout = QFormLayout(cache_group)

        self.cache_check = QCheckBox("Activer le Cache")
        self.cache_check.setChecked(True)
        cache_layout.addRow("Cache des Résultats:", self.cache_check)

        self.cache_clear_btn = QPushButton("🗑️ Vider le Cache")
        cache_layout.addRow("Actions:", self.cache_clear_btn)

        advanced_layout.addWidget(cache_group)
        advanced_layout.addStretch()

        self.tab_widget.addTab(advanced_widget, "⚙️ Avancé")

    def populate_initial_config(self):
        """Remplit les champs avec une configuration initiale."""
        default_config = {
            "model": "Free Space",
            "resolution": 1.0,
            "frequency": "2.4 GHz",
            "reflections": 3,
            "diffraction": True,
            "backend": "default",
            "parallel": True,
        }
        self.set_simulation_config(default_config)

    def set_simulation_config(self, config: dict):
        """
        Met à jour les widgets avec une configuration donnée.
        Args:
            config (dict): Dictionnaire de configuration
        """
        # === AJOUT POUR DIAGNOSTIC ===
        print(f"DEBUG PropertiesPanel.set_simulation_config: Appelé avec config={config}")
        print(f"DEBUG PropertiesPanel.set_simulation_config: Type de config: {type(config)}")
        if isinstance(config, dict):
            for key, value in config.items():
                print(f"  - {key}: {value} (type: {type(value)})")
        # =============================
        self.validate_config_types(config)

        try:
            # --- Simulation Tab ---
            model = config.get("model", "Free Space")
            if hasattr(self, "model_combo") and self.model_combo is not None:
                try:
                    self._safe_set_combobox_text(self.model_combo, model)
                except RuntimeError as re:
                    if "wrapped C/C++ object" in str(re) and "has been deleted" in str(re):
                        print("PropertiesPanel.set_simulation_config: model_combo widget deleted. Skipping update.")
                    else:
                        raise
            else:
                print("model_combo not initialized!")

            resolution = config.get("resolution", 1.0)
            if hasattr(self, "resolution_spin") and self.resolution_spin is not None:
                try:
                    self._safe_set_spinbox_value(self.resolution_spin, resolution)
                except RuntimeError as re:
                    if "wrapped C/C++ object" in str(re) and "has been deleted" in str(
                        re
                    ):
                        print(
                            "PropertiesPanel.set_simulation_config: resolution_spin widget deleted. Skipping update."
                        )
                    else:
                        raise

            frequency = config.get("frequency", "2.4 GHz")
            if hasattr(self, "frequency_combo") and self.frequency_combo is not None:
                try:
                    self._safe_set_combobox_text(self.frequency_combo, frequency)
                except RuntimeError as re:
                    if "wrapped C/C++ object" in str(re) and "has been deleted" in str(
                        re
                    ):
                        print(
                            "PropertiesPanel.set_simulation_config: frequency_combo widget deleted. Skipping update."
                        )
                    else:
                        raise

            reflections = config.get("reflections", 3)
            if hasattr(self, "reflections_spin") and self.reflections_spin is not None:
                try:
                    self._safe_set_spinbox_value(self.reflections_spin, reflections)
                except RuntimeError as re:
                    if "wrapped C/C++ object" in str(re) and "has been deleted" in str(
                        re
                    ):
                        print(
                            "PropertiesPanel.set_simulation_config: reflections_spin widget deleted. Skipping update."
                        )
                    else:
                        raise

            diffraction = config.get("diffraction", True)
            if (
                hasattr(self, "diffractions_check")
                and self.diffractions_check is not None
            ):
                try:
                    self.diffractions_check.setChecked(diffraction)
                except RuntimeError as re:
                    if "wrapped C/C++ object" in str(re) and "has been deleted" in str(
                        re
                    ):
                        print(
                            "PropertiesPanel.set_simulation_config: diffractions_check widget deleted. Skipping update."
                        )
                    else:
                        raise

            backend = config.get("backend", "default")
            if hasattr(self, "backend_combo") and self.backend_combo is not None:
                try:
                    self._safe_set_combobox_text(self.backend_combo, backend)
                except RuntimeError as re:
                    if "wrapped C/C++ object" in str(re) and "has been deleted" in str(
                        re
                    ):
                        print(
                            "PropertiesPanel.set_simulation_config: backend_combo widget deleted. Skipping update."
                        )
                    else:
                        raise

            parallel = config.get("parallel", True)
            if hasattr(self, "parallel_check") and self.parallel_check is not None:
                try:
                    self.parallel_check.setChecked(parallel)
                except RuntimeError as re:
                    if "wrapped C/C++ object" in str(re) and "has been deleted" in str(
                        re
                    ):
                        print(
                            "PropertiesPanel.set_simulation_config: parallel_check widget deleted. Skipping update."
                        )
                    else:
                        raise

            # Ajout pour voxel_size et height_levels si présents
            if "voxel_size" in config:
                if (
                    hasattr(self, "voxel_size_spin")
                    and self.voxel_size_spin is not None
                ):
                    try:
                        self._safe_set_spinbox_value(
                            self.voxel_size_spin, config["voxel_size"]
                        )
                    except RuntimeError as re:
                        if "wrapped C/C++ object" in str(
                            re
                        ) and "has been deleted" in str(re):
                            print(
                                "PropertiesPanel.set_simulation_config: voxel_size_spin widget deleted. Skipping update."
                            )
                        else:
                            raise
            if "height_levels" in config:
                if (
                    hasattr(self, "height_levels_spin")
                    and self.height_levels_spin is not None
                ):
                    try:
                        self._safe_set_spinbox_value(
                            self.height_levels_spin, config["height_levels"]
                        )
                    except RuntimeError as re:
                        if "wrapped C/C++ object" in str(
                            re
                        ) and "has been deleted" in str(re):
                            print(
                                "PropertiesPanel.set_simulation_config: height_levels_spin widget deleted. Skipping update."
                            )
                        else:
                            raise

            if hasattr(self, "status_label") and self.status_label is not None:
                self.status_label.setText("✅ Configuration chargée")

        except Exception as e:
            error_msg = f"Erreur de chargement de config: {e}"
            print(f"PropertiesPanel.set_simulation_config: {error_msg}")
            import traceback

            traceback.print_exc()

    def get_simulation_config(self) -> dict:
        """Récupère la configuration actuelle depuis les widgets."""
        config = {
            "model": self.model_combo.currentText(),
            "resolution": self.resolution_spin.value(),
            "frequency": self.frequency_combo.currentText(),
            "reflections": self.reflections_spin.value(),
            "diffraction": self.diffractions_check.isChecked(),
            "backend": self.backend_combo.currentText(),
            "parallel": self.parallel_check.isChecked(),
            "precision": self.precision_combo.currentText(),
            "voxel_size": self.voxel_size_spin.value(),
        }
        return config

    def load_antenna_properties(self, antenna_data):
        """Charge les propriétés d'une antenne spécifique."""
        try:
            if not antenna_data:
                self.clear_antenna_properties()
                return

            self.current_antenna = antenna_data

            # Activer le groupe et les boutons
            self.antenna_group.setEnabled(True)
            self.apply_antenna_btn.setEnabled(True)
            self.reset_antenna_btn.setEnabled(True)
            self.antenna_info_label.setText(
                "Modification des propriétés de l'antenne sélectionnée."
            )

            # Remplir les champs avec les données de l'antenne
            self.antenna_name_edit.setText(
                getattr(antenna_data, "name", "Antenne Inconnue")
            )
            self.antenna_type_label.setText(getattr(antenna_data, "type", "N/A"))

                # SUPPRESSION DE LA POSITION : ne pas traiter position

            # Fréquence
            frequency = getattr(antenna_data, "frequency", "2.4 GHz")
            if isinstance(frequency, (int, float)):
                # Convertir en texte lisible
                freq_text = (
                    f"{frequency/1e9:.1f} GHz"
                    if frequency >= 1e9
                    else f"{frequency/1e6:.1f} MHz"
                )
            else:
                freq_text = str(frequency)

            freq_index = self.antenna_freq_combo.findText(freq_text)
            if freq_index >= 0:
                self.antenna_freq_combo.setCurrentIndex(freq_index)
            else:
                self.antenna_freq_combo.addItem(freq_text)
                self.antenna_freq_combo.setCurrentText(freq_text)

            # Puissance
            power = getattr(antenna_data, "power_dbm", 20.0)
            self.antenna_power_spin.setValue(float(power))

            # Gain
            gain = getattr(antenna_data, "gain", 5.0)
            self.antenna_gain_spin.setValue(float(gain))

            self.status_label.setText(
                f"✅ Propriétés de '{antenna_data.name}' chargées"
            )

        except Exception as e:
            self.show_error(f"Erreur de chargement de l'antenne: {e}")
            self.clear_antenna_properties()

    def clear_antenna_properties(self):
        """Efface les propriétés de l'antenne."""
        self.current_antenna = None
        self.antenna_group.setEnabled(False)
        self.apply_antenna_btn.setEnabled(False)
        self.reset_antenna_btn.setEnabled(False)
        self.antenna_info_label.setText(
            "Sélectionnez une antenne dans la scène pour modifier ses propriétés."
        )

        # Réinitialiser les champs
        self.antenna_name_edit.clear()
        self.antenna_type_label.setText("N/A")
        # SUPPRESSION DE LA POSITION : ne pas réinitialiser X/Y/Z
        self.antenna_freq_combo.setCurrentIndex(0)
        self.antenna_power_spin.setValue(20.0)
        self.antenna_gain_spin.setValue(5.0)

    def apply_simulation_config(self):
        """Applique la configuration de simulation."""
        try:
            config = self.get_simulation_config()
            self.simulation_config_changed.emit(config)
            self.status_label.setText("✅ Configuration de simulation appliquée")
        except Exception as e:
            self.show_error(f"Erreur d'application de la config: {e}")

    def reset_simulation_config(self):
        """Réinitialise la configuration de simulation."""
        self.populate_initial_config()
        self.status_label.setText("🔄 Configuration réinitialisée")

    def apply_antenna_config(self):
        """Applique la configuration de l'antenne."""
        if not self.current_antenna:
            self.show_warning("Aucune antenne sélectionnée")
            return

        try:
            # Créer un dictionnaire avec les nouvelles propriétés
            new_config = {
                "id": getattr(self.current_antenna, "id", None),
                "name": self.antenna_name_edit.text(),
                    # SUPPRESSION DE LA POSITION
                "frequency": self.antenna_freq_combo.currentText(),
                "power_dbm": self.antenna_power_spin.value(),
                "gain": self.antenna_gain_spin.value(),
            }

            self.antenna_config_changed.emit(new_config)
            self.status_label.setText(
                f"✅ Configuration de '{new_config['name']}' appliquée"
            )

        except Exception as e:
            self.show_error(f"Erreur d'application de l'antenne: {e}")

    def reset_antenna_config(self):
        """Réinitialise la configuration de l'antenne."""
        if self.current_antenna:
            self.load_antenna_properties(self.current_antenna)
            self.status_label.setText("🔄 Configuration antenne réinitialisée")

    def show_error(self, message):
        """Affiche un message d'erreur."""
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        print(f"PropertiesPanel ERREUR: {message}")

    def show_warning(self, message):
        """Affiche un message d'avertissement."""
        self.status_label.setText(f"⚠️ {message}")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        print(f"PropertiesPanel AVERTISSEMENT: {message}")

    def show_info(self, message):
        """Affiche un message d'information."""
        self.status_label.setText(f"ℹ️ {message}")
        self.status_label.setStyleSheet("color: blue;")
        print(f"PropertiesPanel INFO: {message}")


# Pour tester le widget de manière isolée
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Créer un objet antenne de test
    class TestAntenna:
        def __init__(self):
            self.id = "test_001"
            self.name = "Antenne Test"
            self.type = "WiFi"
            self.position = [1.0, 2.0, 3.0]
            self.frequency = "2.4 GHz"
            self.power_dbm = 20.0
            self.gain = 5.0

    # Créer et afficher le panneau
    panel = PropertiesPanel()
    panel.show()

    # Charger une antenne de test
    test_antenna = TestAntenna()
    panel.load_antenna_properties(test_antenna)

    sys.exit(app.exec())
