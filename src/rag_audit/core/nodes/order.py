"""Définition du node du graph LangGraph."""

from langchain_core.messages import ToolMessage

from ..assistant_state import AssistantState
from rag_audit.features.audit import execute_audit


def order_node(state: AssistantState) -> AssistantState:
    """
    The ordering node. This is where the order state is manipulated.
    
    Args:
        state: État de la conversation
        
    Returns:
        État mis à jour
    """
    tool_msg = state.get("messages", [])[-1]
    order = state.get("order", [])
    outbound_msgs = []
    order_placed = False
    
    for tool_call in tool_msg.tool_calls:
        if tool_call["name"] == "add_to_order":
            control_id = tool_call["args"]["control_id"]
            order.append(control_id)
            response = f"✅ Contrôle {control_id} ajouté à la liste d'audit."
            
        elif tool_call["name"] == "confirm_order":
            print("Your audit list:")
            if not order:
                print("  (no controls)")
            for control in order:
                print(f"  {control}")
            response = input("Is this correct? ")
            
        elif tool_call["name"] == "get_order":
            response = "\n".join(order) if order else "(no audit list)"
            
        elif tool_call["name"] == "clear_order":
            order.clear()
            response = "🗑️ Liste d'audit vidée."
            
        elif tool_call["name"] == "place_order":
            order_placed = True
            result = execute_audit(order)
            response = f"🚀 Audit lancé pour {len(order)} contrôles. Résultat: {result.summary}"
        else:
            raise NotImplementedError(f'Unknown tool call: {tool_call["name"]}')
        
        outbound_msgs.append(
            ToolMessage(
                content=response,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    
    return {"messages": outbound_msgs, "order": order, "start_audit": order_placed}
