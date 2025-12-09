# rag_audit/audit_logger.py
"""Logger d'audit pour tracer les événements."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Optional, Dict, Any, List

from ..config.config import DEFAULT_DB_PATH


class AuditLogger:
    """Logger pour tracer les événements d'audit dans SQLite."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else Path(DEFAULT_DB_PATH)
        self._init_db()
    
    def _connect(self):
        return sqlite3.connect(str(self.db_path))
    
    def _init_db(self) -> None:
        with self._connect() as conn:
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
    
    def log_event(
        self,
        role: str,
        message: str,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        context_excerpt: Optional[str] = None,
    ) -> None:
        try:
            tool_args_serialized = json.dumps(tool_args, ensure_ascii=False)
        except Exception:
            try:
                tool_args_serialized = str(tool_args)
            except Exception:
                tool_args_serialized = "<unserializable>"
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO rag_logs 
                (timestamp, role, message, tool_name, tool_args, context_excerpt)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    role,
                    message,
                    tool_name,
                    tool_args_serialized,
                    context_excerpt,
                ),
            )
            conn.commit()
    
    def show_audit_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._connect() as conn:
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
        
        return [
            {"timestamp": ts, "role": role, "message": msg, "tool_name": tool}
            for ts, role, msg, tool in rows
        ]