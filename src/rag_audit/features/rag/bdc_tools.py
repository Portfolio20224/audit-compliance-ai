from langchain_core.tools import tool


def create_retrieve_bdc_tool(vector_store, audit_logger):
    """
    Crée l'outil retrieve_bdc avec accès au VectorStore.
    
    Args:
        vector_store: Instance du VectorStore
        audit_logger: Instance du logger
        
    Returns:
        Fonction outil configurée
    """
    
    @tool
    def retrieve_bdc(query: str) -> str:
        """
        Recherche dans la Base de Connaissance les passages pertinents à partir d'une requête utilisateur.
        Args:
            query : requête utilisateur
            
        Returns:
            Retourne les extraits trouvés.
        
        """
        results = vector_store.get_relevant_documents(query)
        docs = results.get("documents", [[]])[0]
        
        if not docs:
            return "Aucune information pertinente trouvée."
        
        combined = "\n\n".join(docs)
        
        audit_logger.log_event(
            role="tool",
            message="Documents RAG récupérés.",
            tool_name="retrieve_bdc",
            tool_args={"query": query},
            context_excerpt=combined[:500]
        )
        
        return combined
    
    return retrieve_bdc