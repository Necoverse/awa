import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict
import json

class Database:
    def __init__(self, db_path: str = "data/teddy.db"):
        self.db_path = db_path

    async def initialize(self):
        """Veritabanını oluştur"""
        async with aiosqlite.connect(self.db_path) as db:
            # Konuşma geçmişi tablosu
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    audio_path TEXT,
                    video_path TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Kullanıcı profili tablosu
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    preferences TEXT,
                    interaction_history TEXT,
                    last_seen DATETIME
                )
            """)

            # Öğrenilen bilgiler tablosu
            await db.execute("""
                CREATE TABLE IF NOT EXISTS learned_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT,
                    confidence FLOAT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.commit()

    async def save_conversation(self, session_id: str, user_message: str, 
                              assistant_message: str, audio_path: Optional[str] = None,
                              video_path: Optional[str] = None) -> int:
        """Konuşmayı kaydet"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO conversations 
                (session_id, user_message, assistant_message, audio_path, video_path)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_message, assistant_message, audio_path, video_path))
            await db.commit()
            return cursor.lastrowid

    async def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Konuşma geçmişini getir"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (session_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_user_profile(self, user_id: str, preferences: Dict = None,
                                interaction: Dict = None):
        """Kullanıcı profilini güncelle"""
        async with aiosqlite.connect(self.db_path) as db:
            if preferences or interaction:
                # Mevcut profili al
                cursor = await db.execute(
                    "SELECT preferences, interaction_history FROM user_profiles WHERE user_id = ?",
                    (user_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    current_prefs = json.loads(row[0]) if row[0] else {}
                    current_inter = json.loads(row[1]) if row[1] else {}
                    
                    if preferences:
                        current_prefs.update(preferences)
                    if interaction:
                        current_inter.update(interaction)
                    
                    await db.execute("""
                        UPDATE user_profiles 
                        SET preferences = ?, interaction_history = ?, last_seen = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, (json.dumps(current_prefs), json.dumps(current_inter), user_id))
                else:
                    await db.execute("""
                        INSERT INTO user_profiles 
                        (user_id, preferences, interaction_history, last_seen)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """, (user_id, json.dumps(preferences or {}), json.dumps(interaction or {})))
                
                await db.commit()

    async def add_learned_knowledge(self, topic: str, content: str, 
                                  source: Optional[str] = None, 
                                  confidence: float = 1.0):
        """Yeni öğrenilen bilgiyi kaydet"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO learned_knowledge (topic, content, source, confidence)
                VALUES (?, ?, ?, ?)
            """, (topic, content, source, confidence))
            await db.commit()

    async def get_learned_knowledge(self, topic: Optional[str] = None) -> List[Dict]:
        """Öğrenilen bilgileri getir"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if topic:
                cursor = await db.execute(
                    "SELECT * FROM learned_knowledge WHERE topic = ? ORDER BY confidence DESC",
                    (topic,)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM learned_knowledge ORDER BY timestamp DESC"
                )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows] 