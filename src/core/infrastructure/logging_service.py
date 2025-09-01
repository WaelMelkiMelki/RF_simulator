# src/core/infrastructure/logging_service.py
"""
Service de Logging - NETDATA INNOVATION
COUCHE INFRASTRUCTURE - External Services

Responsabilités :
- Configuration centralisée du logging
- Logs structurés pour différents composants
- Rotation automatique des fichiers
- Intégration avec monitoring de performance
"""
import logging
import logging.handlers
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class NetdataFormatter(logging.Formatter):
    """
    Formatter personnalisé pour logs NETDATA.
    
    Ajoute des informations contextuelles et structure JSON.
    """
    
    def __init__(self, include_json=False):
        self.include_json = include_json
        
        if include_json:
            super().__init__()
        else:
            super().__init__(
                fmt='%(asctime)s - %(name)s - %(levelname)s - [%(layer)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    def format(self, record):
        """Formate un enregistrement de log."""
        # Ajouter des informations de couche NETDATA si disponibles
        if not hasattr(record, 'layer'):
            # Détecter la couche à partir du nom du module
            if 'gui' in record.name:
                record.layer = 'PRESENTATION'
            elif 'application' in record.name:
                record.layer = 'APPLICATION'
            elif 'domain' in record.name:
                record.layer = 'DOMAIN'
            elif 'infrastructure' in record.name:
                record.layer = 'INFRASTRUCTURE'
            else:
                record.layer = 'UNKNOWN'
        
        if self.include_json:
            # Format JSON structuré
            log_data = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'layer': record.layer,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Ajouter exception si présente
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            # Ajouter données personnalisées si présentes
            if hasattr(record, 'performance_data'):
                log_data['performance'] = record.performance_data
            
            if hasattr(record, 'simulation_data'):
                log_data['simulation'] = record.simulation_data
            
            return json.dumps(log_data, ensure_ascii=False)
        else:
            # Format texte standard
            return super().format(record)

class LoggingService:
    """
    Service de logging centralisé pour NETDATA INNOVATION.
    
    COUCHE INFRASTRUCTURE - External Services
    Responsabilités :
    - Configuration logging multi-handler
    - Logs rotatifs avec gestion d'espace
    - Intégration métriques de performance
    - Logs structurés JSON pour analyse
    """
    
    def __init__(self, log_dir: str = "logs", max_file_size: int = 10*1024*1024):
        """
        Initialise le service de logging.
        
        Args:
            log_dir: Répertoire des logs
            max_file_size: Taille max par fichier (défaut 10MB)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = max_file_size
        
        # Stockage des loggers configurés
        self.configured_loggers = set()
        
        # Configuration de base
        self._setup_root_logger()
        
        # Créer les loggers spécialisés
        self._setup_specialized_loggers()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("LoggingService: Service de logging NETDATA initialisé")
    
    def _setup_root_logger(self):
        """Configure le logger racine."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Nettoyer les handlers existants
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(NetdataFormatter(include_json=False))
        root_logger.addHandler(console_handler)
        
        # Handler fichier général
        general_file = self.log_dir / "netdata_general.log"
        file_handler = logging.handlers.RotatingFileHandler(
            general_file,
            maxBytes=self.max_file_size,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(NetdataFormatter(include_json=False))
        root_logger.addHandler(file_handler)
        
        # Handler JSON pour analyse
        json_file = self.log_dir / "netdata_structured.jsonl"
        json_handler = logging.handlers.RotatingFileHandler(
            json_file,
            maxBytes=self.max_file_size,
            backupCount=3,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(NetdataFormatter(include_json=True))
        root_logger.addHandler(json_handler)
    
    def _setup_specialized_loggers(self):
        """Configure les loggers spécialisés par couche NETDATA."""
        
        # Logger pour la couche PRESENTATION
        self._create_layer_logger(
            'presentation',
            'netdata_presentation.log',
            ['gui', 'cli', 'adapters']
        )
        
        # Logger pour la couche APPLICATION
        self._create_layer_logger(
            'application', 
            'netdata_application.log',
            ['application', 'orchestrator', 'validator', 'exporter']
        )
        
        # Logger pour la couche DOMAIN
        self._create_layer_logger(
            'domain',
            'netdata_domain.log', 
            ['domain', 'antenna', 'rf_models', 'scene']
        )
        
        # Logger pour la couche INFRASTRUCTURE
        self._create_layer_logger(
            'infrastructure',
            'netdata_infrastructure.log',
            ['infrastructure', 'visualization', 'parallel', 'cache']
        )
        
        # Logger spécialisé pour les performances
        self._create_performance_logger()
        
        # Logger spécialisé pour les simulations
        self._create_simulation_logger()
    
    def _create_layer_logger(self, layer_name: str, filename: str, keywords: list):
        """Crée un logger spécialisé pour une couche."""
        logger_name = f"netdata.{layer_name}"
        logger = logging.getLogger(logger_name)
        
        if logger_name in self.configured_loggers:
            return
        
        logger.setLevel(logging.DEBUG)
        logger.propagate = True  # Propager vers le root logger
        
        # Handler fichier spécialisé
        file_path = self.log_dir / filename
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=self.max_file_size,
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter avec layer info
        formatter = NetdataFormatter(include_json=False)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        self.configured_loggers.add(logger_name)
    
    def _create_performance_logger(self):
        """Crée le logger spécialisé pour les performances."""
        perf_logger = logging.getLogger("netdata.performance")
        
        if "netdata.performance" in self.configured_loggers:
            return
        
        perf_logger.setLevel(logging.DEBUG)
        perf_logger.propagate = False  # Ne pas propager pour éviter les doublons
        
        # Handler fichier performance
        perf_file = self.log_dir / "netdata_performance.log"
        perf_handler = logging.handlers.RotatingFileHandler(
            perf_file,
            maxBytes=self.max_file_size,
            backupCount=10,  # Plus d'historique pour les perfs
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.DEBUG)
        perf_handler.setFormatter(NetdataFormatter(include_json=True))
        
        perf_logger.addHandler(perf_handler)
        self.configured_loggers.add("netdata.performance")
    
    def _create_simulation_logger(self):
        """Crée le logger spécialisé pour les simulations."""
        sim_logger = logging.getLogger("netdata.simulation")
        
        if "netdata.simulation" in self.configured_loggers:
            return
        
        sim_logger.setLevel(logging.INFO)
        sim_logger.propagate = True
        
        # Handler fichier simulation
        sim_file = self.log_dir / "netdata_simulation.log"
        sim_handler = logging.handlers.RotatingFileHandler(
            sim_file,
            maxBytes=self.max_file_size,
            backupCount=5,
            encoding='utf-8'
        )
        sim_handler.setLevel(logging.INFO)
        sim_handler.setFormatter(NetdataFormatter(include_json=False))
        
        sim_logger.addHandler(sim_handler)
        self.configured_loggers.add("netdata.simulation")
    
    def get_logger(self, name: str, layer: Optional[str] = None) -> logging.Logger:
        """
        Récupère un logger configuré pour NETDATA.
        
        Args:
            name: Nom du logger
            layer: Couche NETDATA (presentation, application, domain, infrastructure)
            
        Returns:
            Logger configuré
        """
        if layer:
            logger_name = f"netdata.{layer}.{name}"
        else:
            logger_name = name
        
        logger = logging.getLogger(logger_name)
        
        # Ajouter l'attribut layer pour le formatter
        if layer:
            # Créer un adapter pour ajouter automatiquement la couche
            class LayerLoggerAdapter(logging.LoggerAdapter):
                def process(self, msg, kwargs):
                    return msg, kwargs
                
                def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
                    if extra is None:
                        extra = {}
                    extra['layer'] = layer.upper()
                    super()._log(level, msg, args, exc_info, extra, stack_info)
            
            return LayerLoggerAdapter(logger, {})
        
        return logger
    
    def log_performance_metrics(self, component: str, metrics: Dict[str, Any]):
        """Log spécialisé pour les métriques de performance."""
        perf_logger = logging.getLogger("netdata.performance")
        
        # Créer un record avec données de performance
        record = logging.LogRecord(
            name="netdata.performance",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"Performance metrics for {component}",
            args=(),
            exc_info=None
        )
        
        record.performance_data = {
            'component': component,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        perf_logger.handle(record)
    
    def log_simulation_event(self, event_type: str, data: Dict[str, Any]):
        """Log spécialisé pour les événements de simulation."""
        sim_logger = logging.getLogger("netdata.simulation")
        
        record = logging.LogRecord(
            name="netdata.simulation",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"Simulation event: {event_type}",
            args=(),
            exc_info=None
        )
        
        record.simulation_data = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        sim_logger.handle(record)
    
    def get_log_files_info(self) -> Dict[str, Dict[str, Any]]:
        """Retourne des informations sur les fichiers de log."""
        log_files = {}
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                stat = log_file.stat()
                log_files[log_file.name] = {
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'path': str(log_file)
                }
            except Exception as e:
                log_files[log_file.name] = {'error': str(e)}
        
        return log_files
    
    def cleanup_old_logs(self, max_age_days: int = 30) -> int:
        """Nettoie les anciens fichiers de log."""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0
        
        # Chercher les fichiers de log rotatifs
        for log_file in self.log_dir.glob("*.log.*"):
            try:
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except Exception as e:
                self.logger.warning(f"Erreur suppression {log_file}: {e}")
        
        if deleted_count > 0:
            self.logger.info(f"LoggingService: {deleted_count} anciens logs supprimés")
        
        return deleted_count
    
    def set_log_level(self, logger_name: str, level: str):
        """Change le niveau de log d'un logger."""
        logger = logging.getLogger(logger_name)
        level_obj = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(level_obj)
        
        self.logger.info(f"LoggingService: Niveau de {logger_name} changé vers {level}")
    
    def get_logging_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du service de logging."""
        stats = {
            'configured_loggers': len(self.configured_loggers),
            'log_directory': str(self.log_dir),
            'max_file_size_mb': self.max_file_size / (1024 * 1024),
            'log_files': self.get_log_files_info()
        }
        
        return stats

# Instance globale du service de logging
_logging_service = None

def get_logging_service() -> LoggingService:
    """Retourne l'instance globale du service de logging."""
    global _logging_service
    
    if _logging_service is None:
        _logging_service = LoggingService()
    
    return _logging_service

def get_netdata_logger(name: str, layer: Optional[str] = None) -> logging.Logger:
    """
    Fonction utilitaire pour obtenir un logger NETDATA.
    
    Args:
        name: Nom du logger
        layer: Couche NETDATA (optionnel)
        
    Returns:
        Logger configuré
    """
    service = get_logging_service()
    return service.get_logger(name, layer)

# Configuration par défaut au chargement du module
if _logging_service is None:
    _logging_service = LoggingService()
