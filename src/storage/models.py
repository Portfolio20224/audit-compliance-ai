import sqlite3
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
import json
from pathlib import Path


DEFAULT_DB_PATH = Path("rag_audit.db")


class AuditLogger:
    """Gestionnaire des logs d'audit dans une base SQLite."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialise la base de données SQLite si elle n'existe pas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                role TEXT,
                message TEXT,
                tool_name TEXT,
                tool_args TEXT,
                context_excerpt TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def log_event(
        self,
        role: str,
        message: str,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        context_excerpt: Optional[str] = None,
    ) -> None:
        """Enregistre un événement dans la base de données."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO rag_logs 
            (timestamp, role, message, tool_name, tool_args, context_excerpt)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                #datetime.utcnow().isoformat()
                datetime.now(UTC).isoformat(),
                role,
                message,
                tool_name,
                json.dumps(tool_args) if tool_args else None,
                context_excerpt,
            ),
        )

        conn.commit()
        conn.close()

    def show_audit_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les derniers logs d'audit."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, role, message, tool_name 
            FROM rag_logs 
            ORDER BY id DESC 
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "timestamp": ts,
                "role": role,
                "message": msg,
                "tool_name": tool,
            }
            for ts, role, msg, tool in rows
        ]
