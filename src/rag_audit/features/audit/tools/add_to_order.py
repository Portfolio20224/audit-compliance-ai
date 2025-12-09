# rag_audit/tools.py
"""Définition des outils LangChain."""

from langchain_core.tools import tool


@tool
def add_to_order(control_id: str) -> str:
    """
    Ajouter un contrôle à la liste d'audit.
    
    Args:
        control_id : Référence du contrôle ISO 27001
        
    Returns:
        Message de confirmation
    """
    pass