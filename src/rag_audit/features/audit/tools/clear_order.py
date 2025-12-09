from langchain_core.tools import tool


@tool
def clear_order() -> str:
    """
    Supprime tous les contrôles de la liste d'audit de l'utilisateur.
    
    Returns:
        Message de confirmation
    """
    pass