import chromadb
from chromadb.config import Settings
from typing import Dict, Any
import json

class VectorStore:
    def __init__(self, persist_directory: str = "./chromadb"):
        """
        Initialise le client ChromaDB et les collections.

        Paramerters:
            - persist_directory : le chemin d'enregistrement
        """
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        self.analysis_collection = self._create_collection("analysis")
        self.evidence_collection = self._create_collection("evidence")
        self.report_collection = self._create_collection("report")

    def _create_collection(self, name: str):
        """Crée une collection Chroma si elle n'existe pas déjà."""
        return self.client.get_or_create_collection(name=name)

    def _doc_text_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Compose un document lisible à partir du JSON d'analyse"""
        parts = [
            f"Exigence: {analysis.get('requirement')}",
            f"Verdict: {analysis.get('verdict')}",
            f"Score: {analysis.get('score')}",
            "Justification:",
            analysis.get("justification", ""),
            "Preuves utilisées:",
            json.dumps(analysis.get("evidence_used", {}), ensure_ascii=False, indent=2),
            "Recommandations:",
            "\n".join(analysis.get("recommendations", []))
        ]
        return "\n\n".join([p for p in parts if p])
    
    def analysis_exists(self, requirement: str) -> bool:
        """Vérifie si une analyse existe déjà pour une exigence"""
        results = self.analysis_collection.get(
            where={"requirement": requirement},
            limit=1
        )
        return len(results["ids"]) > 0
    
    def add_analysis(self, analysis: Dict[str, Any], update_existing: bool = True) -> None:
        """
        Ajoute ou met à jour une analyse structurée.
        """
        requirement = analysis.get('requirement')
        
        if self.analysis_exists(requirement):
            if update_existing:
                self._update_analysis(requirement, analysis)
                return
            else:
                raise ValueError(f"Analyse déjà existante pour: {requirement}")
        
        doc = self._doc_text_from_analysis(analysis)
        metadata = {
            "requirement": requirement,
            "verdict": analysis.get("verdict"),
            "score": analysis.get("score")
        }
        self.analysis_collection.add(
            documents=[doc],
            metadatas=[metadata],
            ids=[f"analysis::{requirement}"]
        )
    
    def _update_analysis(self, requirement: str, analysis: Dict[str, Any]) -> None:
        """Met à jour une analyse existante"""
        doc = self._doc_text_from_analysis(analysis)
        metadata = {
            "requirement": requirement,
            "verdict": analysis.get("verdict"),
            "score": analysis.get("score")
        }
        self.analysis_collection.update(
            ids=[f"analysis::{requirement}"],
            documents=[doc],
            metadatas=[metadata]
        )
    
    def _doc_text_from_evidence(self, requirement: str, evidence: Dict[str, Any]) -> str:
        """Compose un document pour les preuves"""
        parts = [f"Exigence: {requirement}", json.dumps(evidence, ensure_ascii=False, indent=2)]
        return "\n\n".join(parts)
    
    def add_evidence(self, requirement: str, evidence: Dict[str, Any]) -> None:
        """Ajoute des preuves dans la collection 'evidence'."""
        doc = self._doc_text_from_evidence(requirement, evidence)
        metadata = {"requirement": requirement}
        self.evidence_collection.add(
            documents=[doc],
            metadatas=[metadata],
            ids=[f"evidence::{requirement}"]
        )
    
    def add_report_section(self, section_id: str, title: str, content: str) -> None:
        """Ajoute une section de rapport"""
        doc = f"# {title}\n\n{content}"
        metadata = {"section_id": section_id, "title": title}
        self.report_collection.add(
            documents=[doc],
            metadatas=[metadata],
            ids=[f"report::{section_id}"]
        )

    def search_analysis(self, query: str, n_results: int = 5) -> None:
        """Recherche sémantique dans les analyses."""
        return self.analysis_collection.query(
            query_texts=[query],
            n_results=n_results
        )

    def search_evidence(self, query: str, n_results: int = 5):
        """Recherche sémantique dans les preuves."""
        return self.evidence_collection.query(
            query_texts=[query],
            n_results=n_results
        )

    def search_report(self, query: str, n_results: int = 5):
        """Recherche sémantique dans les sections du rapport."""
        return self.report_collection.query(
            query_texts=[query],
            n_results=n_results
        )