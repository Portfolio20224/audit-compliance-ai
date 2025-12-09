# tests/test_models.py
"""Tests pour les modèles de données."""

from src.rag_audit.features.audit import ControlItem, AuditResult


def test_control_item_creation():
    """Test la création d'un ControlItem."""
    control = ControlItem(control_id="A.5.1", description="Access control")
    assert control.control_id == "A.5.1"
    assert control.description == "Access control"


def test_control_item_no_description():
    """Test la création d'un ControlItem sans description."""
    control = ControlItem(control_id="A.5.1")
    assert control.control_id == "A.5.1"
    assert control.description is None


def test_audit_result_creation():
    """Test la création d'un AuditResult."""
    result = AuditResult(
        success=True,
        details={"A.5.1": {"verdict": "OK"}},
        summary="Test completed"
    )
    assert result.success is True
    assert "A.5.1" in result.details
    assert result.summary == "Test completed"