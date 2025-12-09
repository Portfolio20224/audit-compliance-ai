# rag_audit/tools.py
"""Définition des outils LangChain."""

from langchain_core.tools import tool

@tool
def get_order() -> str:
    """
    Récupère la liste d'audit actuelle.
    
    Returns:
        Un contrôle par ligne.
    """
    pass

