import os
import sqlite3
import json
import hashlib
import pickle
from pathlib import Path
from datetime import datetime

class SimulationCache:
    def close(self):
        """Ferme explicitement la connexion SQLite si elle existe (pour compatibilité Windows)."""
        # Cette classe utilise des connexions contextuelles, mais on peut prévoir une future connexion persistante
        # Si jamais une connexion persistante est ajoutée, fermer ici
        pass
    def __init__(self, cache_dir="cache", max_size_mb=500):
        self.cache_dir = cache_dir  # Utilise le setter pour garantir Path
        self.max_size = max_size_mb * 1024 * 1024
        self.db_path = self.cache_dir / "cache_metadata.db"
        self._init_db()

    @property
    def cache_dir(self):
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value):
        self._cache_dir = Path(value)
        self._cache_dir.mkdir(exist_ok=True)
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    size INTEGER,
                    last_accessed TIMESTAMP,
                    params_hash TEXT
                )
            """)
    def _get_cache_size(self):
        return sum(f.stat().st_size for f in self.cache_dir.glob('*.cache'))
    def _make_space(self, required_size):
        current_size = self._get_cache_size()
        if current_size + required_size <= self.max_size:
            return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key, size FROM cache_entries
                ORDER BY last_accessed ASC
            """)
            for key, size in cursor.fetchall():
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    cache_file.unlink()
                    conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                    current_size -= size
                    if current_size + required_size <= self.max_size:
                        break
    def generate_key(self, simulation_params):
        params_str = json.dumps(simulation_params, sort_keys=True)
        return hashlib.sha256(params_str.encode()).hexdigest()
    def get_cached_results(self, params):
        key = self.generate_key(params)
        cache_file = self.cache_dir / f"{key}.cache"
        if not cache_file.exists():
            return None
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE cache_entries
                SET last_accessed = ?
                WHERE key = ?
            """, (datetime.now(), key))
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    def cache_results(self, params, results):
        key = self.generate_key(params)
        cache_file = self.cache_dir / f"{key}.cache"
        with open(cache_file, 'wb') as f:
            pickle.dump(results, f)
        file_size = cache_file.stat().st_size
        self._make_space(file_size)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache_entries (key, size, last_accessed, params_hash)
                VALUES (?, ?, ?, ?)
            """, (key, file_size, datetime.now(), json.dumps(params)))
    def clear_cache(self):
        for file in self.cache_dir.glob('*.cache'):
            file.unlink()
        # Vider la table au lieu de supprimer le fichier DB (compatible Windows)
        if self.db_path.exists():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache_entries")
        self._init_db()
