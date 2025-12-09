"""Construction du graph LangGraph sous forme de classe."""

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI

from ..assistant_state import AssistantState
from rag_audit.features.audit.tools import add_to_order, confirm_order, get_order, clear_order, place_order
from ..nodes import human_node, order_node, chatbot
from ..routing import maybe_exit_human_node, maybe_route_to_tools
from rag_audit.infrastructure.logging import AuditLogger
from rag_audit.features.rag import VectorStore, create_retrieve_bdc_tool


class LangGraphBuilder:
    """
    Classe encapsulant la construction du graph LangGraph.
    """

    def __init__(self, vector_store: VectorStore, audit_logger: AuditLogger, model_name: str = "gemini-2.0-flash"):
        self.vector_store = vector_store
        self.audit_logger = audit_logger
        self.model_name = model_name

        self.graph_builder = StateGraph(AssistantState)

        self.llm_with_tools = None
        self.tool_node = None

        self._setup_graph()

    def _setup_graph(self):
        """
        Prépare la structure du graph LangGraph (nodes et edges).
        """

        # Initialiser le LLM
        llm = ChatGoogleGenerativeAI(model=self.model_name)

        # Créer l'outil retrieve_bdc
        retrieve_bdc_tool = create_retrieve_bdc_tool(self.vector_store, self.audit_logger)

        # Auto-tools
        auto_tools = [retrieve_bdc_tool]
        self.tool_node = ToolNode(auto_tools)

        # Order-tools
        order_tools = [add_to_order, confirm_order, get_order, clear_order, place_order]

        # LLM avec outils
        self.llm_with_tools = llm.bind_tools(auto_tools + order_tools)

        # Nodes
        self.graph_builder.add_node("chatbot", self._chatbot_wrapper)
        self.graph_builder.add_node("human", self._human_node_wrapper)
        self.graph_builder.add_node("tools", self.tool_node)
        self.graph_builder.add_node("auditing", order_node)

        # Edges
        self.graph_builder.add_conditional_edges("chatbot", self._maybe_route_to_tools_wrapper)
        self.graph_builder.add_conditional_edges("human", maybe_exit_human_node)

        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.add_edge("auditing", "chatbot")
        self.graph_builder.add_edge(START, "chatbot")

    # ---- Wrappers (en méthodes privées) ----

    def _human_node_wrapper(self, state: AssistantState):
        return human_node(state, self.audit_logger)

    def _chatbot_wrapper(self, state:AssistantState):
        return chatbot(state, self.llm_with_tools, self.audit_logger)

    def _maybe_route_to_tools_wrapper(self, state:AssistantState):
        return maybe_route_to_tools(state, self.tool_node)

    # ---- Sortie finale ----

    def get_graph(self):
        return self.graph_builder.compile()
