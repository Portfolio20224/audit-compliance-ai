"""Service d'exécution des audits."""

import time
from typing import List

from .models import AuditResult


def run_compliance_audit(order: List[str]) -> AuditResult:
    """
    Mock d'un process d'audit. Remplace par un appel réel asynchrone ou sync.
    
    Args:
        order: Liste des contrôles à auditer
        
    Returns:
        Résultat de l'audit
    """
    if not order:
        return AuditResult(
            success=False,
            details={},
            summary="No controls specified."
        )
    
    time.sleep(0.1 * len(order))
    
    details = {c: {"verdict": "OK", "score": 0.95} for c in order}
    return AuditResult(
        success=True,
        details=details,
        summary=f"Audit terminé pour {len(order)} contrôles."
    )


def execute_audit(order: List[str]) -> AuditResult:
    """
    Wrapper pour séparer l'interface d'exécution.
    
    Args:
        order: Liste des contrôles à auditer
        
    Returns:
        Résultat de l'audit
    """
    return run_compliance_audit(order)