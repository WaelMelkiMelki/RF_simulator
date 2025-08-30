# src/gui/widgets/performance_panel.py
"""
Panneau de performance pour surveiller les ressources système et l'état de la simulation.
Affiche les rapports de performance, l'utilisation mémoire et permet la gestion du cache.
"""

import sys
import os
from pathlib import Path

# Ajout du chemin src si nécessaire
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QPushButton, QTextEdit, QProgressBar, QComboBox,
    QMessageBox, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class PerformancePanel(QWidget):
    """
    Widget pour afficher les performances et gérer les ressources système.
    Surveille l'utilisation CPU, mémoire, cache et fournit des outils de gestion.
    """
    
    # Signaux
    cache_cleared = pyqtSignal()  # Émis quand le cache est vidé
    
    def __init__(self, orchestrator=None, parent=None):
        """
        Initialise le panneau de performance.
        
        Args:
            orchestrator: Instance de SimulationOrchestrator (optionnel)
            parent: Widget parent Qt
        """
        super().__init__(parent)
        self.orchestrator = orchestrator
        self.parent_window = parent
        self.monitoring_enabled = True
        
        self.init_ui()
        self.setup_timers()
        self.start_monitoring()
        
    def init_ui(self):
        """Initialise l'interface utilisateur du panneau de performance."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Titre
        title_label = QLabel("📊 Performance & Ressources")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Créer les groupes de monitoring
        self.create_system_monitor_group()
        self.create_performance_report_group()
        self.create_cache_management_group()
        
        # Barre de statut
        self.status_label = QLabel(" Surveillance active")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: green; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Boutons de contrôle global
        control_layout = QHBoxLayout()
        
        self.toggle_monitor_btn = QPushButton("⏸️ Pause")
        self.toggle_monitor_btn.clicked.connect(self.toggle_monitoring)
        control_layout.addWidget(self.toggle_monitor_btn)
        
        self.refresh_btn = QPushButton("🔄 Rafraîchir")
        self.refresh_btn.clicked.connect(self.refresh_all)
        control_layout.addWidget(self.refresh_btn)
        
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
    def create_system_monitor_group(self):
        """Crée le groupe de monitoring système."""
        self.system_group = QGroupBox("🖥️ Système")
        system_layout = QFormLayout(self.system_group)
        
        # CPU Usage
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setValue(0)
        self.cpu_progress.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        system_layout.addRow("CPU:", self.cpu_progress)
        
        # Memory Usage
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setValue(0)
        self.memory_progress.setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }")
        system_layout.addRow("Mémoire:", self.memory_progress)
        
        # Cache Status
        self.cache_label = QLabel("N/A")
        system_layout.addRow("Cache:", self.cache_label)
        
        # Simulation Status
        self.sim_status_label = QLabel("Inactif")
        self.sim_status_label.setStyleSheet("color: gray;")
        system_layout.addRow("Simulation:", self.sim_status_label)
        
        self.layout().addWidget(self.system_group)
        
    def create_performance_report_group(self):
        """Crée le groupe d'affichage des rapports de performance."""
        self.report_group = QGroupBox("📈 Rapport de Performance")
        report_layout = QVBoxLayout(self.report_group)
        
        # Options de filtrage
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filtre:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tout", "Calculs RF", "Cache", "IO", "Autre"])
        self.filter_combo.currentTextChanged.connect(self.filter_reports)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        
        refresh_mini_btn = QPushButton("🔄")
        refresh_mini_btn.setMaximumWidth(30)
        refresh_mini_btn.clicked.connect(self.refresh_report)
        filter_layout.addWidget(refresh_mini_btn)
        
        report_layout.addLayout(filter_layout)
        
        # Zone de texte pour les rapports
        self.report_box = QTextEdit()
        self.report_box.setReadOnly(True)
        self.report_box.setMinimumHeight(150)
        self.report_box.setFont(QFont("Consolas", 9))
        report_layout.addWidget(self.report_box)
        
        self.layout().addWidget(self.report_group)
        
    def create_cache_management_group(self):
        """Crée le groupe de gestion du cache."""
        self.cache_group = QGroupBox("キャッシング")
        cache_layout = QVBoxLayout(self.cache_group)
        
        # Statistiques du cache
        stats_layout = QFormLayout()
        self.cache_size_label = QLabel("0 Mo")
        stats_layout.addRow("Taille:", self.cache_size_label)
        
        self.cache_entries_label = QLabel("0 entrées")
        stats_layout.addRow("Entrées:", self.cache_entries_label)
        
        self.cache_hits_label = QLabel("0 hits")
        stats_layout.addRow("Hits:", self.cache_hits_label)
        
        self.cache_miss_label = QLabel("0 misses")
        stats_layout.addRow("Misses:", self.cache_miss_label)
        
        cache_layout.addLayout(stats_layout)
        
        # Boutons de gestion
        cache_btn_layout = QHBoxLayout()
        
        self.clear_cache_btn = QPushButton("🗑️ Vider le cache")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        cache_btn_layout.addWidget(self.clear_cache_btn)
        
        self.clear_old_btn = QPushButton("🧹 Nettoyer vieux")
        self.clear_old_btn.clicked.connect(self.clear_old_cache)
        cache_btn_layout.addWidget(self.clear_old_btn)
        
        cache_btn_layout.addStretch()
        
        cache_layout.addLayout(cache_btn_layout)
        
        self.layout().addWidget(self.cache_group)
        
    def setup_timers(self):
        """Configure les timers pour le rafraîchissement automatique."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all)
        self.refresh_timer.setInterval(2000)  # Rafraîchir toutes les 2 secondes
        
    def start_monitoring(self):
        """Démarre la surveillance automatique."""
        if self.monitoring_enabled:
            self.refresh_timer.start()
            self.status_label.setText(" Surveillance active")
            self.status_label.setStyleSheet("color: green; font-style: italic;")
            self.toggle_monitor_btn.setText("⏸️ Pause")
            
    def stop_monitoring(self):
        """Arrête la surveillance automatique."""
        self.refresh_timer.stop()
        self.status_label.setText(" Surveillance en pause")
        self.status_label.setStyleSheet("color: orange; font-style: italic;")
        self.toggle_monitor_btn.setText("▶️ Reprendre")
        
    def toggle_monitoring(self):
        """Bascule l'état de la surveillance."""
        if self.monitoring_enabled:
            self.stop_monitoring()
            self.monitoring_enabled = False
        else:
            self.start_monitoring()
            self.monitoring_enabled = True
            
    def refresh_all(self):
        """Rafraîchit toutes les informations de performance."""
        try:
            self.refresh_system_monitor()
            self.refresh_report()
            self.refresh_cache_stats()
        except Exception as e:
            print(f"PerformancePanel.refresh_all: Erreur: {e}")
            
    def refresh_system_monitor(self):
        """Rafraîchit les indicateurs système."""
        try:
            # Simuler l'utilisation CPU/Mémoire (à remplacer par de vraies mesures)
            import random
            cpu_usage = random.randint(10, 80)
            memory_usage = random.randint(20, 70)
            
            self.cpu_progress.setValue(cpu_usage)
            self.memory_progress.setValue(memory_usage)
            
            # Mettre à jour les labels avec des valeurs simulées
            self.cpu_progress.setFormat(f"{cpu_usage}%")
            self.memory_progress.setFormat(f"{memory_usage}%")
            
            # Mettre à jour le statut de simulation
            if self.orchestrator:
                if hasattr(self.orchestrator, 'is_running') and self.orchestrator.is_running:
                    self.sim_status_label.setText("En cours...")
                    self.sim_status_label.setStyleSheet("color: orange; font-weight: bold;")
                else:
                    self.sim_status_label.setText("Inactif")
                    self.sim_status_label.setStyleSheet("color: gray;")
                    
        except Exception as e:
            print(f"PerformancePanel.refresh_system_monitor: Erreur: {e}")
            
    def refresh_report(self):
        """Rafraîchit le rapport de performance."""
        try:
            report_content = ""
            
            # Obtenir le rapport depuis le PerformanceMonitor si disponible
            if self.orchestrator and hasattr(self.orchestrator, 'performance_monitor'):
                try:
                    report = self.orchestrator.performance_monitor.get_report()
                    if isinstance(report, dict):
                        # Formater le rapport dict
                        for task, metrics in report.items():
                            duration = metrics.get('duration', 'N/A')
                            report_content += f"⏱️ {task}: {duration}s\n"
                    elif isinstance(report, str):
                        report_content = report
                    else:
                        report_content = str(report)
                except Exception as e:
                    report_content = f"⚠️ Erreur PerformanceMonitor: {e}\n"
            else:
                # Rapport simulé
                report_content = "ℹ️ Aucun PerformanceMonitor disponible\n"
                report_content += "📈 Simulation démarrée à 14:30:25\n"
                report_content += "⏱️ Calcul RF: 2.3s (1000 points)\n"
                report_content += "💾 Cache hit: 85%\n"
                
            # Ajouter l'utilisation mémoire si disponible
            if self.orchestrator and hasattr(self.orchestrator, 'memory_manager'):
                try:
                    mem_info = self.orchestrator.memory_manager.get_memory_usage()
                    if isinstance(mem_info, dict):
                        rss_mb = mem_info.get('rss', 0) // (1024 * 1024)
                        percent = mem_info.get('percent', 0)
                        report_content += f"\n🧠 Mémoire: {rss_mb} MB ({percent:.1f}%)"
                except Exception as e:
                    report_content += f"\n⚠️ Erreur mémoire: {e}"
                    
            self.report_box.setPlainText(report_content)
            
        except Exception as e:
            error_msg = f"Erreur lors du rafraîchissement du rapport: {e}"
            print(f"PerformancePanel.refresh_report: {error_msg}")
            self.report_box.setPlainText(f"❌ {error_msg}")
            
    def filter_reports(self, filter_text):
        """Filtre les rapports affichés selon le critère sélectionné."""
        # Cette méthode peut être implémentée pour filtrer le contenu
        # du QTextEdit selon le filtre sélectionné
        print(f"PerformancePanel.filter_reports: Filtrage par '{filter_text}'")
        self.refresh_report()  # Pour l'instant, on rafraîchit tout
        
    def refresh_cache_stats(self):
        """Rafraîchit les statistiques du cache."""
        try:
            cache_info = {
                'size_mb': 0,
                'entries': 0,
                'hits': 0,
                'misses': 0
            }
            
            # Obtenir les infos depuis le cache si disponible
            if self.orchestrator and hasattr(self.orchestrator, 'cache'):
                try:
                    # Simuler des statistiques de cache
                    import random
                    cache_info['size_mb'] = random.randint(10, 100)
                    cache_info['entries'] = random.randint(5, 50)
                    cache_info['hits'] = random.randint(100, 500)
                    cache_info['misses'] = random.randint(10, 100)
                    
                    # Mettre à jour les labels
                    self.cache_size_label.setText(f"{cache_info['size_mb']} Mo")
                    self.cache_entries_label.setText(f"{cache_info['entries']} entrées")
                    self.cache_hits_label.setText(f"{cache_info['hits']} hits")
                    self.cache_miss_label.setText(f"{cache_info['misses']} misses")
                    self.cache_label.setText(f"{cache_info['entries']} entrées")
                    
                except Exception as e:
                    self.cache_label.setText(f"⚠️ Erreur: {e}")
            else:
                self.cache_label.setText("N/A")
                
        except Exception as e:
            print(f"PerformancePanel.refresh_cache_stats: Erreur: {e}")
            
    def clear_cache(self):
        """Vide complètement le cache."""
        try:
            if self.orchestrator and hasattr(self.orchestrator, 'cache'):
                # Confirmation
                reply = QMessageBox.question(
                    self,
                    "Confirmation",
                    "Êtes-vous sûr de vouloir vider complètement le cache ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.orchestrator.cache.clear_cache()
                    self.show_info("Cache vidé avec succès")
                    self.refresh_cache_stats()
                    self.cache_cleared.emit()
            else:
                self.show_warning("Aucun cache disponible à vider")
                
        except Exception as e:
            error_msg = f"Erreur lors du vidage du cache: {e}"
            print(f"PerformancePanel.clear_cache: {error_msg}")
            self.show_error(error_msg)
            
    def clear_old_cache(self):
        """Nettoie les entrées de cache anciennes."""
        try:
            if self.orchestrator and hasattr(self.orchestrator, 'cache'):
                # Implémentation factice - à remplacer par la vraie logique
                self.show_info("Nettoyage des entrées de cache anciennes (simulation)")
                self.refresh_cache_stats()
            else:
                self.show_warning("Aucun cache disponible à nettoyer")
                
        except Exception as e:
            error_msg = f"Erreur lors du nettoyage du cache: {e}"
            print(f"PerformancePanel.clear_old_cache: {error_msg}")
            self.show_error(error_msg)
            
    def show_error(self, message):
        """
        Affiche un message d'erreur.
        
        Args:
            message: Message d'erreur à afficher
        """
        print(f"PerformancePanel ERREUR: {message}")
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(f"❌ {message}", 5000)
                
    def show_warning(self, message):
        """
        Affiche un message d'avertissement.
        
        Args:
            message: Message d'avertissement à afficher
        """
        print(f"PerformancePanel AVERTISSEMENT: {message}")
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(f"⚠️ {message}", 3000)
                
    def show_info(self, message):
        """
        Affiche un message d'information.
        
        Args:
            message: Message d'information à afficher
        """
        print(f"PerformancePanel INFO: {message}")
        if hasattr(self, 'parent_window') and self.parent_window:
            if hasattr(self.parent_window, 'status_bar'):
                self.parent_window.status_bar.showMessage(f"ℹ️ {message}", 2000)

# Pour tester le widget de manière isolée
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Créer un orchestrateur factice pour le test
    class FakeOrchestrator:
        def __init__(self):
            self.is_running = False
            class FakeCache:
                def clear_cache(self):
                    print("Cache vidé")
            self.cache = FakeCache()
            
            class FakeMemoryManager:
                def get_memory_usage(self):
                    return {'rss': 50 * 1024 * 1024, 'percent': 25.0}
            self.memory_manager = FakeMemoryManager()
            
            class FakePerformanceMonitor:
                def get_report(self):
                    return "⏱️ Tâche 1: 1.2s\n⏱️ Tâche 2: 0.8s"
            self.performance_monitor = FakePerformanceMonitor()
    
    # Créer et afficher le panneau
    panel = PerformancePanel(orchestrator=FakeOrchestrator())
    panel.show()
    
    sys.exit(app.exec())