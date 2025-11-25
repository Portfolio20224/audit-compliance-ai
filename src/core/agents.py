from typing import Optional
from ..storage.models import AuditLogger
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..tools.collect_tools import (
    collect_system_logs,
    collect_hr_policies,
    collect_cloud_configurations,
)
from ..storage.vectorstore import VectorStore


class ComplianceAgents:
    """
    Gestionnaire d'agents spécialisés en audit de conformité :
    - Collecte de preuves
    - Analyse JSON des exigences
    - Rédaction de rapports Markdown
    - Assistance conversationnelle
    """

    def __init__(
        self,
        llm_instance: Optional[ChatGoogleGenerativeAI] = None,
        vectorstore: Optional[VectorStore] = None,
        audit_logger : Optional[AuditLogger] = None
    ):
        self.llm = llm_instance or ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.vectorstore = vectorstore or VectorStore()
        self.audit_logger = audit_logger or AuditLogger()
        self.collector_tools = [
            collect_system_logs,
            collect_hr_policies,
            collect_cloud_configurations,
        ]

        self.audit_logger.log_event(
            role="system",
            message="ComplianceAgents initialized",
            tool_name=None,
        )

    def create_collector_agent(self) -> AgentExecutor:
        """
        Crée l'Agent Collecteur chargé de :
        - collecter les preuves via les outils
        - structurer les données récupérées
        """
        self.audit_logger.log_event(
            role="system",
            message="Collector agent created",
            tool_name="collector_agent"
        )

        collector_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=(
                "Vous êtes un Agent Collecteur expert en cybersécurité.\n"
                "Votre rôle:\n"
                "1. Collecter les preuves nécessaires pour l'exigence fournie\n"
                "2. Utiliser les outils appropriés\n"
                "3. Structurer les preuves collectées\n\n"
                "Répondez avec un résumé structuré."
            )),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_tool_calling_agent(self.llm, self.collector_tools, collector_prompt)
        return AgentExecutor(agent=agent, tools=self.collector_tools, verbose=True)

    def create_analyst_agent(self):
        """
        Crée l'Agent Analyste chargé de produire une analyse JSON stricte.
        """
        self.audit_logger.log_event(
            role="system",
            message="Analyst agent created",
            tool_name="analyst_agent"
        )
        analyst_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=(
                "Vous êtes un Agent Analyste expert en audit de conformité.\n"
                "Produisez STRICTEMENT un JSON au format suivant:\n\n"
                "{\n"
                '  "requirement": "<id>",\n'
                '  "verdict": "Conforme|Non-Conforme|Partiellement Conforme",\n'
                "  \"score\": <0-100>,\n"
                "  \"justification\": \"<texte>\",\n"
                "  \"evidence_used\": <objet>,\n"
                "  \"recommendations\": [\"...\"]\n"
                "}\n\n"
                "Ne fournissez rien d'autre."
            )),
            MessagesPlaceholder(variable_name="messages")
        ])
        return analyst_prompt | self.llm

    def create_reporter_agent(self):
        """
        Crée l'Agent Rédacteur chargé de générer un rapport Markdown.
        """
        self.audit_logger.log_event(
            role="system",
            message="Reporter agent created",
            tool_name="reporter_agent"
        )
        reporter_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=(
                "Vous êtes un Agent Rédacteur expert en audit.\n"
                "Générez un rapport final en Markdown uniquement."
            )),
            MessagesPlaceholder(variable_name="messages")
        ])
        return reporter_prompt | self.llm

    def create_assistant_agent(self):
        """
        Crée l'assistant conversationnel général dédié à la conformité.
        """
        assistant_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=(
                "Vous êtes un Assistant d'Audit conversationnel. "
                "Répondez de manière précise et utile sur les exigences de conformité."
            )),
            MessagesPlaceholder(variable_name="messages")
        ])
        return assistant_prompt | self.llm
