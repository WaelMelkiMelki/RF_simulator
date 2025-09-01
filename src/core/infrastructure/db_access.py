# src/core/infrastructure/db_access.py
"""
Service d'Accès Base de Données - NETDATA INNOVATION
COUCHE INFRASTRUCTURE - Data Access

Responsabilités :
- Accès aux bases de données de propriétés matériaux
- Stockage des configurations d'antennes
- Cache persistant des calculs RF
- Gestion des métadonnées de simulation
"""
import logging
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class DatabaseAccess:
    """
    Service d'accès aux bases de données NETDATA.
    
    COUCHE INFRASTRUCTURE - Data Access
    Responsabilités :
    - Gestion des connexions SQLite
    - Stockage/récupération des propriétés matériaux
    - Cache persistant des calculs RF
    - Métadonnées des simulations
    """
    
    def __init__(self, db_path: str = "data/netdata.db"):
        """Initialise le service d'accès base de données."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connexion à la base de données
        self.connection = None
        
        self._init_database()
        logger.info(f"DatabaseAccess: Initialisé avec {self.db_path}")
    
    def _init_database(self):
        """Initialise la structure de la base de données."""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Pour les résultats en dictionnaire
            
            # Créer les tables si elles n'existent pas
            self._create_tables()
            
            # Insérer les données par défaut
            self._insert_default_materials()
            
            logger.info("DatabaseAccess: Base de données initialisée")
            
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur initialisation DB: {e}")
            raise
    
    def _create_tables(self):
        """Crée les tables de la base de données."""
        cursor = self.connection.cursor()
        
        # Table des propriétés de matériaux
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                permittivity REAL NOT NULL,
                conductivity REAL NOT NULL,
                loss_tangent REAL NOT NULL,
                frequency_range TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des configurations d'antennes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS antenna_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                frequency REAL NOT NULL,
                gain REAL NOT NULL,
                pattern_data TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table du cache RF
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rf_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                result_data TEXT NOT NULL,
                frequency REAL,
                power REAL,
                scene_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        """)
        
        # Table des métadonnées de simulation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulation_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                scene_file TEXT,
                config_data TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT,
                results_summary TEXT
            )
        """)
        
        self.connection.commit()
        logger.info("DatabaseAccess: Tables créées")
    
    def _insert_default_materials(self):
        """Insère les matériaux par défaut."""
        default_materials = [
            {
                'name': 'concrete',
                'permittivity': 6.5,
                'conductivity': 0.01,
                'loss_tangent': 0.1,
                'frequency_range': '100MHz-10GHz',
                'description': 'Béton standard pour construction'
            },
            {
                'name': 'wood',
                'permittivity': 2.5,
                'conductivity': 0.001,
                'loss_tangent': 0.05,
                'frequency_range': '100MHz-10GHz',
                'description': 'Bois sec standard'
            },
            {
                'name': 'metal',
                'permittivity': 1.0,
                'conductivity': 1e6,
                'loss_tangent': 0.0,
                'frequency_range': 'DC-THz',
                'description': 'Métal conducteur parfait'
            },
            {
                'name': 'glass',
                'permittivity': 6.0,
                'conductivity': 1e-12,
                'loss_tangent': 0.01,
                'frequency_range': '100MHz-100GHz',
                'description': 'Verre standard'
            }
        ]
        
        cursor = self.connection.cursor()
        
        for material in default_materials:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO materials 
                    (name, permittivity, conductivity, loss_tangent, frequency_range, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    material['name'],
                    material['permittivity'], 
                    material['conductivity'],
                    material['loss_tangent'],
                    material['frequency_range'],
                    material['description']
                ))
            except sqlite3.IntegrityError:
                pass  # Matériau déjà existant
        
        self.connection.commit()
        logger.info(f"DatabaseAccess: {len(default_materials)} matériaux par défaut insérés")
    
    def get_material_properties(self, material_name: str) -> Optional[Dict[str, Any]]:
        """Récupère les propriétés d'un matériau."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM materials WHERE name = ?
            """, (material_name,))
            
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            else:
                logger.warning(f"DatabaseAccess: Matériau '{material_name}' non trouvé")
                return None
                
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur récupération matériau: {e}")
            return None
    
    def get_all_materials(self) -> List[Dict[str, Any]]:
        """Récupère tous les matériaux disponibles."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM materials ORDER BY name")
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur récupération matériaux: {e}")
            return []
    
    def save_antenna_config(self, name: str, antenna_type: str, frequency: float,
                           gain: float, pattern_data: Dict, properties: Dict) -> bool:
        """Sauvegarde une configuration d'antenne."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO antenna_configs 
                (name, type, frequency, gain, pattern_data, properties)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name, antenna_type, frequency, gain,
                json.dumps(pattern_data), json.dumps(properties)
            ))
            
            self.connection.commit()
            logger.info(f"DatabaseAccess: Configuration antenne '{name}' sauvegardée")
            return True
            
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur sauvegarde antenne: {e}")
            return False
    
    def get_antenna_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupère une configuration d'antenne."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM antenna_configs WHERE name = ?
            """, (name,))
            
            row = cursor.fetchone()
            
            if row:
                config = dict(row)
                config['pattern_data'] = json.loads(config['pattern_data'])
                config['properties'] = json.loads(config['properties'])
                return config
            else:
                return None
                
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur récupération config antenne: {e}")
            return None
    
    def cache_rf_result(self, cache_key: str, result_data: Dict,
                       frequency: float, power: float, scene_hash: str) -> bool:
        """Met en cache un résultat de calcul RF."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO rf_cache 
                (cache_key, result_data, frequency, power, scene_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (
                cache_key, json.dumps(result_data),
                frequency, power, scene_hash
            ))
            
            self.connection.commit()
            logger.debug(f"DatabaseAccess: Résultat RF mis en cache: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur cache RF: {e}")
            return False
    
    def get_cached_rf_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Récupère un résultat RF du cache."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT result_data FROM rf_cache WHERE cache_key = ?
            """, (cache_key,))
            
            row = cursor.fetchone()
            
            if row:
                # Incrémenter le compteur d'accès
                cursor.execute("""
                    UPDATE rf_cache 
                    SET access_count = access_count + 1 
                    WHERE cache_key = ?
                """, (cache_key,))
                self.connection.commit()
                
                return json.loads(row['result_data'])
            else:
                return None
                
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur récupération cache RF: {e}")
            return None
    
    def save_simulation_metadata(self, session_id: str, scene_file: str,
                                config_data: Dict, status: str = "started") -> bool:
        """Sauvegarde les métadonnées d'une simulation."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO simulation_metadata 
                (session_id, scene_file, config_data, start_time, status)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
            """, (
                session_id, scene_file,
                json.dumps(config_data), status
            ))
            
            self.connection.commit()
            logger.info(f"DatabaseAccess: Métadonnées simulation sauvegardées: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur sauvegarde métadonnées: {e}")
            return False
    
    def update_simulation_status(self, session_id: str, status: str,
                                results_summary: Optional[Dict] = None) -> bool:
        """Met à jour le statut d'une simulation."""
        try:
            cursor = self.connection.cursor()
            
            if results_summary:
                cursor.execute("""
                    UPDATE simulation_metadata 
                    SET status = ?, end_time = CURRENT_TIMESTAMP, results_summary = ?
                    WHERE session_id = ?
                """, (status, json.dumps(results_summary), session_id))
            else:
                cursor.execute("""
                    UPDATE simulation_metadata 
                    SET status = ?
                    WHERE session_id = ?
                """, (status, session_id))
            
            self.connection.commit()
            logger.info(f"DatabaseAccess: Statut simulation mis à jour: {session_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur mise à jour statut: {e}")
            return False
    
    def cleanup_old_cache(self, max_age_days: int = 30) -> int:
        """Nettoie les anciens résultats du cache."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                DELETE FROM rf_cache 
                WHERE created_at < datetime('now', '-{} days')
            """.format(max_age_days))
            
            deleted_count = cursor.rowcount
            self.connection.commit()
            
            logger.info(f"DatabaseAccess: {deleted_count} entrées de cache supprimées")
            return deleted_count
            
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur nettoyage cache: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, int]:
        """Retourne les statistiques de la base de données."""
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            # Compter les matériaux
            cursor.execute("SELECT COUNT(*) FROM materials")
            stats['materials_count'] = cursor.fetchone()[0]
            
            # Compter les configurations d'antennes
            cursor.execute("SELECT COUNT(*) FROM antenna_configs")
            stats['antenna_configs_count'] = cursor.fetchone()[0]
            
            # Compter les entrées de cache
            cursor.execute("SELECT COUNT(*) FROM rf_cache")
            stats['cache_entries_count'] = cursor.fetchone()[0]
            
            # Compter les simulations
            cursor.execute("SELECT COUNT(*) FROM simulation_metadata")
            stats['simulations_count'] = cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur statistiques DB: {e}")
            return {}
    
    def close(self):
        """Ferme la connexion à la base de données."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                logger.info("DatabaseAccess: Connexion fermée")
        except Exception as e:
            logger.error(f"DatabaseAccess: Erreur fermeture DB: {e}")
    
    def __del__(self):
        """Destructeur - ferme la connexion."""
        self.close()
