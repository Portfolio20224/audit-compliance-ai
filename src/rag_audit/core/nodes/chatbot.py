"""Définition des nodes du graph LangGraph."""

from langchain_core.messages import AIMessage

from ..assistant_state import AssistantState
from ..prompts import BOT_SYSINT, WELCOME_MSG
from rag_audit.infrastructure.logging import AuditLogger

def chatbot(state: AssistantState, llm_with_tools, audit_logger:AuditLogger) -> AssistantState:
    """
    Chatbot intelligent instrumenté avec logs pour appels outils et stockage SQLite.
    
    Args:
        state: État de la conversation
        llm_with_tools: LLM configuré avec les outils
        audit_logger: Instance du logger
        
    Returns:
        État mis à jour
    """
    # Vérifier si des messages existent
    if not state["messages"]:
        # If there are no messages, start with the welcome message.
        new_output = AIMessage(content=WELCOME_MSG)
        audit_logger.log_event(role="assistant", message=WELCOME_MSG)
        return {"messages": [new_output]}
    
    # Cas normal : traiter le dernier message utilisateur
    last_message = state["messages"][-1]
    user_message = last_message.content
    
    audit_logger.log_event(role="user", message=user_message)
    
    message_history = [BOT_SYSINT] + state["messages"]
    response = llm_with_tools.invoke(message_history)
    
    audit_logger.log_event(role="assistant", message=response.content)
    
    # Si le modèle déclenche un outil
    if hasattr(response, "tool_calls") and response.tool_calls:
        for call in response.tool_calls:
            audit_logger.log_event(
                role="assistant",
                message="Appel d'outil",
                tool_name=call["name"],
                tool_args=call["args"]
            )
    
    return {"messages": [response]}