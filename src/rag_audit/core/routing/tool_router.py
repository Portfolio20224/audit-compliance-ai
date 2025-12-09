"""Fonctions de routage pour le graph LangGraph."""

from langgraph.graph import END
from ..assistant_state import AssistantState


def maybe_route_to_tools(state: AssistantState, tool_node) -> str:
    """
    Route between chat and tool nodes if a tool call is made.
    
    Args:
        state: État de la conversation
        tool_node: ToolNode pour vérifier les outils disponibles
        
    Returns:
        Nom du prochain node
    """
    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")
    
    msg = msgs[-1]
    
    # Si l'audit est lancé, terminer l'application
    if state.get("start_audit", False):
        return END
    
    # Si des outils sont appelés
    elif hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        # Vérifier si c'est un outil RAG (retrieve_bdc)
        if any(
            tool["name"] in tool_node.tools_by_name for tool in msg.tool_calls
        ):
            return "tools"  # Route vers le ToolNode RAG
        else:
            return "auditing"  # Route vers order_node
    
    # Par défaut, aller vers l'humain
    else:
        return "human"