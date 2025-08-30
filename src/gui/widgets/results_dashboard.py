# src/gui/widgets/results_dashboard.py
"""
Tableau de bord des résultats pour le RF Simulator 3D.
Affiche les résultats de simulation dans un format clair et interactif.
"""

import sys
import os
from pathlib import Path

# Ajout du chemin src si nécessaire
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QTextEdit, QProgressBar, QGroupBox, QSplitter,
    QPushButton, QTabWidget, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class ResultsDashboard(QWidget):
    """
    Widget pour afficher les résultats de simulation.
    Présente les données sous forme de tableaux, statistiques et logs.
    """
    
    def __init__(self, parent=None):
        """
        Initialise le tableau de bord des résultats.
        
        Args:
            parent: Widget parent Qt
        """
        super().__init__(parent)
        self.parent_window = parent
        self.current_results = None
        self.init_ui()
        
    def init_ui(self):
        """Initialise l'interface utilisateur du tableau de bord."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Titre
        title_label = QLabel("📊 Tableau de Résultats")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Créer les onglets pour différentes vues
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # --- Onglet Statistiques ---
        self.create_statistics_tab()
        
        # --- Onglet Données Brutes ---
        self.create_raw_data_tab()
        
        # --- Onglet Logs ---
        self.create_logs_tab()
        
        # --- Barre de progression ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # --- Zone de statut ---
        self.status_label = QLabel("Aucun résultat disponible")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)
        
    def create_statistics_tab(self):
        """Crée l'onglet des statistiques."""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        # Groupe des statistiques générales
        general_group = QGroupBox("Statistiques Générales")
        general_layout = QGridLayout(general_group)
        
        self.stats_labels = {}
        stats_data = [
            ("Nombre de points calculés", "points_count"),
            ("Signal minimum (dBm)", "min_signal"),
            ("Signal maximum (dBm)", "max_signal"),
            ("Signal moyen (dBm)", "avg_signal"),
            ("Zone de couverture (%)", "coverage_percent")
        ]
        
        for i, (label_text, key) in enumerate(stats_data):
            # Label de description
            desc_label = QLabel(label_text + ":")
            desc_label.setStyleSheet("font-weight: bold;")
            general_layout.addWidget(desc_label, i, 0)
            
            # Valeur
            value_label = QLabel("N/A")
            value_label.setObjectName(key)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            general_layout.addWidget(value_label, i, 1)
            
            self.stats_labels[key] = value_label
            
        stats_layout.addWidget(general_group)
        
        # Groupe des antennes
        self.antennas_group = QGroupBox("Antennes")
        self.antennas_layout = QVBoxLayout(self.antennas_group)
        self.antennas_layout.addWidget(QLabel("Aucune antenne détectée"))
        stats_layout.addWidget(self.antennas_group)
        
        stats_layout.addStretch()
        
        self.tab_widget.addTab(stats_widget, "📈 Statistiques")
        
    def create_raw_data_tab(self):
        """Crée l'onglet des données brutes."""
        raw_widget = QWidget()
        raw_layout = QVBoxLayout(raw_widget)
        
        # Tableau des résultats
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "X (m)", "Y (m)", "Z (m)", "Signal (dBm)", "Qualité"
        ])
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        raw_layout.addWidget(self.results_table)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        export_csv_btn = QPushButton("📤 Exporter CSV")
        export_csv_btn.clicked.connect(self.export_to_csv)
        button_layout.addWidget(export_csv_btn)
        
        export_vtk_btn = QPushButton("📦 Exporter VTK")
        export_vtk_btn.clicked.connect(self.export_to_vtk)
        button_layout.addWidget(export_vtk_btn)
        
        button_layout.addStretch()
        
        clear_btn = QPushButton("🗑️ Effacer")
        clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(clear_btn)
        
        raw_layout.addLayout(button_layout)
        
        self.tab_widget.addTab(raw_widget, "📋 Données Brutes")
        
    def create_logs_tab(self):
        """Crée l'onglet des logs."""
        logs_widget = QWidget()
        logs_layout = QVBoxLayout(logs_widget)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setMaximumHeight(150)
        logs_layout.addWidget(self.logs_text)
        
        # Boutons pour les logs
        log_button_layout = QHBoxLayout()
        clear_logs_btn = QPushButton("🗑️ Effacer Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        log_button_layout.addWidget(clear_logs_btn)
        
        save_logs_btn = QPushButton("💾 Sauvegarder Logs")
        save_logs_btn.clicked.connect(self.save_logs)
        log_button_layout.addWidget(save_logs_btn)
        
        log_button_layout.addStretch()
        logs_layout.addLayout(log_button_layout)
        
        self.tab_widget.addTab(logs_widget, "📝 Logs")
        
    def display_results(self, results):
        """
        Affiche les résultats de simulation dans le tableau de bord.
        
        Args:
            results: Dictionnaire contenant les résultats de simulation
        """
        try:
            print(f"ResultsDashboard.display_results: Méthode appelée avec des résultats de type {type(results)}")
            
            if not isinstance(results, dict):
                print("ResultsDashboard.display_results: Les résultats ne sont pas un dictionnaire")
                self.show_error("Format de résultats invalide")
                return
                
            # Stocker les résultats
            self.current_results = results
            
            # Mettre à jour les statistiques
            self.update_statistics(results)
            
            # Mettre à jour le tableau de données
            self.update_raw_data_table(results)
            
            # Mettre à jour les logs
            self.update_logs(results)
            
            # Mettre à jour le statut
            if 'coverage' in results and isinstance(results['coverage'], list):
                point_count = len(results['coverage'])
                self.status_label.setText(f"✅ {point_count} points de couverture calculés")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.status_label.setText("⚠️ Résultats incomplets")
                self.status_label.setStyleSheet("color: orange;")
                
            print("ResultsDashboard.display_results: Résultats affichés avec succès")
            
        except Exception as e:
            error_msg = f"Erreur lors de l'affichage des résultats: {e}"
            print(f"ResultsDashboard.display_results: {error_msg}")
            import traceback
            traceback.print_exc()
            self.show_error(error_msg)
    
    def update_statistics(self, results):
        """
        Met à jour les statistiques affichées.
        
        Args:
            results: Dictionnaire des résultats
        """
        try:
            # Extraire les données de couverture
            coverage_data = results.get('coverage', [])
            
            if not coverage_data:
                print("ResultsDashboard.update_statistics: Aucune donnée de couverture trouvée")
                return
                
            # Calculer les statistiques
            signal_strengths = [point.get('signal_strength', 0) for point in coverage_data]
            
            if signal_strengths:
                min_signal = min(signal_strengths)
                max_signal = max(signal_strengths)
                avg_signal = sum(signal_strengths) / len(signal_strengths)
                
                # Mettre à jour les labels
                self.stats_labels['points_count'].setText(str(len(coverage_data)))
                self.stats_labels['min_signal'].setText(f"{min_signal:.2f}")
                self.stats_labels['max_signal'].setText(f"{max_signal:.2f}")
                self.stats_labels['avg_signal'].setText(f"{avg_signal:.2f}")
                
                # Calculer le pourcentage de couverture (> -80 dBm considéré comme bon)
                good_coverage_count = sum(1 for s in signal_strengths if s > -80)
                coverage_percent = (good_coverage_count / len(signal_strengths)) * 100
                self.stats_labels['coverage_percent'].setText(f"{coverage_percent:.1f}%")
                
            # Mettre à jour les informations sur les antennes
            antennas = results.get('antennas', [])
            if antennas:
                # Effacer le layout existant
                for i in reversed(range(self.antennas_layout.count())): 
                    widget = self.antennas_layout.itemAt(i).widget()
                    if widget:
                        widget.deleteLater()
                        
                # Ajouter les nouvelles antennes
                for i, antenna in enumerate(antennas):
                    antenna_label = QLabel(
                        f"📡 Antenne {i+1}: {antenna.get('name', 'Inconnue')} "
                        f"({antenna.get('frequency', 'N/A')})"
                    )
                    self.antennas_layout.addWidget(antenna_label)
            else:
                # Message par défaut
                self.antennas_layout.addWidget(QLabel("Aucune antenne détectée"))
                
        except Exception as e:
            print(f"ResultsDashboard.update_statistics: Erreur: {e}")
            
    def update_raw_data_table(self, results):
        """
        Met à jour le tableau des données brutes.
        
        Args:
            results: Dictionnaire des résultats
        """
        try:
            coverage_data = results.get('coverage', [])
            
            # Configurer le tableau
            self.results_table.setRowCount(len(coverage_data))
            
            # Remplir le tableau
            for row, point in enumerate(coverage_data):
                position = point.get('position', [0, 0, 0])
                signal = point.get('signal_strength', 0)
                
                # Colonnes X, Y, Z
                self.results_table.setItem(row, 0, QTableWidgetItem(f"{position[0]:.2f}"))
                self.results_table.setItem(row, 1, QTableWidgetItem(f"{position[1]:.2f}"))
                self.results_table.setItem(row, 2, QTableWidgetItem(f"{position[2]:.2f}"))
                
                # Colonne Signal
                signal_item = QTableWidgetItem(f"{signal:.2f}")
                if signal > -60:
                    signal_item.setBackground(QColor(144, 238, 144))  # Vert clair
                elif signal > -80:
                    signal_item.setBackground(QColor(255, 255, 224))  # Jaune clair
                else:
                    signal_item.setBackground(QColor(255, 182, 193))  # Rouge clair
                self.results_table.setItem(row, 3, signal_item)
                
                # Colonne Qualité
                if signal > -60:
                    quality = "Excellente"
                elif signal > -70:
                    quality = "Bonne"
                elif signal > -80:
                    quality = "Moyenne"
                else:
                    quality = "Faible"
                self.results_table.setItem(row, 4, QTableWidgetItem(quality))
                
        except Exception as e:
            print(f"ResultsDashboard.update_raw_data_table: Erreur: {e}")
            
    def update_logs(self, results):
        """
        Met à jour les logs affichés.
        
        Args:
            results: Dictionnaire des résultats
        """
        try:
            # Ajouter des informations de base
            log_text = f"=== Résultats de Simulation ===\n"
            log_text += f"Date: {results.get('timestamp', 'Inconnue')}\n"
            log_text += f"Points calculés: {len(results.get('coverage', []))}\n"
            
            # Ajouter des métadonnées si disponibles
            metadata = results.get('metadata', {})
            if metadata:
                log_text += "\n=== Métadonnées ===\n"
                for key, value in metadata.items():
                    log_text += f"{key}: {value}\n"
                    
            self.logs_text.setPlainText(log_text)
            
        except Exception as e:
            print(f"ResultsDashboard.update_logs: Erreur: {e}")
            
    def export_to_csv(self):
        """Exporte les résultats au format CSV."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import csv
            
            if not self.current_results or 'coverage' not in self.current_results:
                self.show_warning("Aucun résultat à exporter")
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter en CSV",
                "resultats_simulation.csv",
                "Fichiers CSV (*.csv)"
            )
            
            if file_path:
                coverage_data = self.current_results['coverage']
                
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['x', 'y', 'z', 'signal_strength', 'quality']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for point in coverage_data:
                        position = point.get('position', [0, 0, 0])
                        signal = point.get('signal_strength', 0)
                        
                        # Déterminer la qualité
                        if signal > -60:
                            quality = "Excellente"
                        elif signal > -70:
                            quality = "Bonne"
                        elif signal > -80:
                            quality = "Moyenne"
                        else:
                            quality = "Faible"
                            
                        writer.writerow({
                            'x': f"{position[0]:.2f}",
                            'y': f"{position[1]:.2f}",
                            'z': f"{position[2]:.2f}",
                            'signal_strength': f"{signal:.2f}",
                            'quality': quality
                        })
                        
                self.status_label.setText(f"✅ Résultats exportés vers {os.path.basename(file_path)}")
                
        except Exception as e:
            self.show_error(f"Erreur d'export CSV: {e}")
            
    def export_to_vtk(self):
        """Exporte les résultats au format VTK."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            if not self.current_results or 'coverage' not in self.current_results:
                self.show_warning("Aucun résultat à exporter")
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter en VTK",
                "resultats_simulation.vtk",
                "Fichiers VTK (*.vtk)"
            )
            
            if file_path:
                # Vérifier si PyVista est disponible
                try:
                    import pyvista as pv
                    import numpy as np
                    
                    # Créer un nuage de points PyVista
                    coverage_data = self.current_results['coverage']
                    positions = np.array([point['position'] for point in coverage_data])
                    signal_strengths = np.array([point['signal_strength'] for point in coverage_data])
                    
                    cloud = pv.PolyData(positions)
                    cloud['signal_strength'] = signal_strengths
                    
                    # Sauvegarder
                    cloud.save(file_path)
                    
                    self.status_label.setText(f"✅ Résultats exportés vers {os.path.basename(file_path)}")
                    
                except ImportError:
                    self.show_error("PyVista non disponible pour l'export VTK")
                except Exception as e:
                    self.show_error(f"Erreur d'export VTK: {e}")
                    
        except Exception as e:
            self.show_error(f"Erreur d'export VTK: {e}")
            
    def clear_results(self):
        """Efface tous les résultats affichés."""
        try:
            # Effacer les statistiques
            for label in self.stats_labels.values():
                label.setText("N/A")
                
            # Effacer le tableau
            self.results_table.setRowCount(0)
            
            # Effacer les logs
            self.logs_text.clear()
            
            # Réinitialiser le statut
            self.status_label.setText("Aucun résultat disponible")
            self.status_label.setStyleSheet("color: gray;")
            
            # Effacer les résultats stockés
            self.current_results = None
            
            print("ResultsDashboard.clear_results: Résultats effacés")
            
        except Exception as e:
            print(f"ResultsDashboard.clear_results: Erreur: {e}")
            
    def clear_logs(self):
        """Efface les logs affichés."""
        self.logs_text.clear()
        
    def save_logs(self):
        """Sauvegarde les logs dans un fichier."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Sauvegarder les logs",
                "logs_simulation.txt",
                "Fichiers texte (*.txt)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.toPlainText())
                    
                self.status_label.setText(f"✅ Logs sauvegardés vers {os.path.basename(file_path)}")
                
        except Exception as e:
            self.show_error(f"Erreur de sauvegarde des logs: {e}")
            
    def show_error(self, message):
        """
        Affiche un message d'erreur.
        
        Args:
            message: Message d'erreur à afficher
        """
        print(f"ResultsDashboard ERREUR: {message}")
        self.status_label.setText(f"❌ ERREUR: {message}")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
    def show_warning(self, message):
        """
        Affiche un message d'avertissement.
        
        Args:
            message: Message d'avertissement à afficher
        """
        print(f"ResultsDashboard AVERTISSEMENT: {message}")
        self.status_label.setText(f"⚠️  {message}")
        self.status_label.setStyleSheet("color: orange;")
        
    def show_info(self, message):
        """
        Affiche un message d'information.
        
        Args:
            message: Message d'information à afficher
        """
        print(f"ResultsDashboard INFO: {message}")
        self.status_label.setText(f"ℹ️  {message}")
        self.status_label.setStyleSheet("color: blue;")

# Pour tester le widget de manière isolée
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Créer des résultats de test
    test_results = {
        "timestamp": "2023-01-01 12:00:00",
        "coverage": [
            {"position": [0, 0, 1], "signal_strength": -50.0},
            {"position": [1, 0, 1], "signal_strength": -55.0},
            {"position": [0, 1, 1], "signal_strength": -60.0},
            {"position": [1, 1, 1], "signal_strength": -65.0},
        ],
        "antennas": [
            {"name": "Antenne Test", "frequency": "2.4GHz"}
        ],
        "metadata": {
            "resolution": "1.0m",
            "model": "Free Space"
        }
    }
    
    # Créer et afficher le dashboard
    dashboard = ResultsDashboard()
    dashboard.show()
    dashboard.display_results(test_results)
    
    sys.exit(app.exec())