"""Fonctions de routage pour le graph LangGraph."""

from typing import Literal
from langgraph.graph import END

from ..assistant_state import AssistantState


def maybe_exit_human_node(state: AssistantState) -> Literal["chatbot", "__end__"]:
    """
    Route to the chatbot, unless it looks like the user is exiting.
    
    Args:
        state: État de la conversation
        
    Returns:
        Nom du prochain node ou END
    """
    if state.get("start_audit", False):
        return END
    else:
        return "chatbot"

