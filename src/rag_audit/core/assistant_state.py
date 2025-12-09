"""Définition de l'état de la conversation."""

from typing import Dict, List, Any, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AssistantState(TypedDict):
    """State représentant la conversation d'audit avec le client."""
    
    messages: Annotated[list, add_messages]
    order: List[str]
    start_audit: bool
    audit_result: Optional[Dict]