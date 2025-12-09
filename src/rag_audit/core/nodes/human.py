"""Définition de l'interaction utilisateur du graph LangGraph."""


from ..assistant_state import AssistantState
from rag_audit.infrastructure.logging import AuditLogger


def human_node(state: AssistantState, audit_logger: AuditLogger) -> AssistantState:
    """
    Display the last model message to the user, and receive the user's input.
    
    Args:
        state: État de la conversation
        audit_logger: Instance du logger
        
    Returns:
        État mis à jour
    """
    last_msg = state["messages"][-1]
    audit_logger.log_event(role="assistant", message=f"Model: {last_msg.content}")
    
    user_input = input("User: ")
    
    # If it looks like the user is trying to quit, flag the conversation as over.
    if user_input in {"q", "quit", "exit", "goodbye"}:
        state["start_audit"] = True
    
    return state | {"messages": [("user", user_input)]}

