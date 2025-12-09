# tests/test_audit_service.py
"""Tests pour le service d'audit."""

from src.rag_audit.features.audit import run_compliance_audit, execute_audit


def test_run_compliance_audit_empty():
    """Test avec une liste vide."""
    result = run_compliance_audit([])
    assert result.success is False
    assert result.summary == "No controls specified."


def test_run_compliance_audit_success():
    """Test avec des contrôles."""
    controls = ["A.5.1", "A.5.2", "A.6.1"]
    result = run_compliance_audit(controls)
    
    assert result.success is True
    assert len(result.details) == 3
    assert "A.5.1" in result.details
    assert result.details["A.5.1"]["verdict"] == "OK"
    assert result.summary == "Audit terminé pour 3 contrôles."


def test_execute_audit():
    """Test du wrapper execute_audit."""
    controls = ["A.5.1"]
    result = execute_audit(controls)
    
    assert result.success is True
    assert len(result.details) == 1