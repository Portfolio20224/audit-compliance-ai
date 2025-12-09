"""Modèles de données pour l'audit."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ControlItem:
    """Représente un contrôle ISO 27001."""
    control_id: str
    description: Optional[str] = None


@dataclass
class AuditResult:
    """Résultat d'un audit."""
    success: bool
    details: Dict[str, Any]
    summary: Optional[str] = None