# rag_audit/tools.py
"""Définition des outils LangChain."""

from langchain_core.tools import tool

@tool
def confirm_order() -> str:
    """
    Demande à l'utilisateur si la liste d'audit actuelle est correcte.
    
    Returns:
        Résumé de la commande
    """
    pass
