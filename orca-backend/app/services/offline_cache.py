import sqlite3
import json
import time
import os

CACHE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "offline_cache.db")

class OfflineCache:
    def __init__(self, db_path=CACHE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data TEXT,
                    timestamp REAL
                )
            ''')
            conn.commit()

    def set(self, key: str, data: dict | list):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO cache (key, data, timestamp)
                VALUES (?, ?, ?)
            ''', (key, json.dumps(data), time.time()))
            conn.commit()

    def get(self, key: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT data, timestamp FROM cache WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0]), row[1]
            return None, None
