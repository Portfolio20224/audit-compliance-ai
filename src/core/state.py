from typing import Dict, List, Any, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Représente l'état interne du workflow d'audit automatisé.
    Utilisé pour synchroniser les agents (Evidence, Analysis, Reporting).
    """

    messages: Annotated[List[Any], add_messages]

    audit_framework: str
    compliance_requirements: List[str]
    collected_evidence: Dict[str, Any]
    analysis_results: Dict[str, Dict[str, Any]]
    report_sections: Dict[str, str]
    final_report: Optional[str]
    current_requirement: str
    audit_progress: float
    errors: List[str]


class AssistantState(TypedDict):
    """
    Représente l'état de la conversation entre le client et l'assistant.
    (Niveau "interface utilisateur")
    """

    messages: Annotated[List[Any], add_messages]
    order: List[str]
    start_audit: bool
    audit_result: Optional[Dict[str, Any]]
