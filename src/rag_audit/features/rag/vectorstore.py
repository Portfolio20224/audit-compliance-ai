# rag_audit/vector_store.py
"""Gestion du stockage vectoriel avec ChromaDB."""

import json
from typing import Dict, Any, List
from pathlib import Path
import chromadb
from chromadb.config import Settings

from rag_audit.infrastructure.config.config import DEFAULT_VECTOR_STORE_PATH


class VectorStore:
    """Gestionnaire de stockage vectoriel pour les documents d'audit."""
    
    def __init__(self, persist_directory: str = DEFAULT_VECTOR_STORE_PATH):
        self.persist_directory = Path(persist_directory)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        self.analysis_collection = self.client.get_or_create_collection("analysis")
        self.evidence_collection = self.client.get_or_create_collection("evidence")
        self.report_collection = self.client.get_or_create_collection("report")
    
    def _doc_text_from_analysis(self, analysis: Dict[str, Any]) -> str:
        parts = [
            f"Exigence: {analysis.get('requirement')}",
            f"Verdict: {analysis.get('verdict')}",
            f"Score: {analysis.get('score')}",
            "Justification:",
            analysis.get("justification", ""),
            "Preuves utilisées:",
            json.dumps(analysis.get("evidence_used", {}), ensure_ascii=False, indent=2),
            "Recommandations:",
            "\n".join(analysis.get("recommendations", []) or [])
        ]
        return "\n\n".join([p for p in parts if p])
    
    def add_analysis(self, analysis: Dict[str, Any], update_existing: bool = True) -> None:
        req = analysis.get("requirement")
        if not req:
            raise ValueError("requirement missing")
        
        id_ = f"analysis::{req}"
        doc = self._doc_text_from_analysis(analysis)
        metadata = {
            "requirement": req,
            "verdict": analysis.get("verdict"),
            "score": analysis.get("score")
        }
        
        existing = self.analysis_collection.get(where={"requirement": req}, limit=1)
        if existing and existing.get("ids"):
            if update_existing:
                self.analysis_collection.update(
                    ids=[id_],
                    documents=[doc],
                    metadatas=[metadata]
                )
                return
            else:
                raise ValueError("Exists")
        
        self.analysis_collection.add(
            documents=[doc],
            metadatas=[metadata],
            ids=[id_]
        )
    
    def add_evidence(self, requirement: str, evidence: Dict[str, Any]) -> None:
        doc = f"Exigence: {requirement}\n\n{json.dumps(evidence, ensure_ascii=False, indent=2)}"
        id_ = f"evidence::{requirement}"
        self.evidence_collection.add(
            documents=[doc],
            metadatas=[{"requirement": requirement}],
            ids=[id_]
        )
    
    def add_report_section(self, section_id: str, title: str, content: str) -> None:
        doc = f"# {title}\n\n{content}"
        id_ = f"report::{section_id}"
        self.report_collection.add(
            documents=[doc],
            metadatas=[{"section_id": section_id, "title": title}],
            ids=[id_]
        )
    
    def get_relevant_documents(self, question: str, k: int = 1) -> Dict[str, List]:
        sources = [
            self.evidence_collection,
            self.analysis_collection,
            self.report_collection
        ]
        all_docs, all_ids, all_dists, all_metas = [], [], [], []
        
        for col in sources:
            res = col.query(query_texts=[question], n_results=k)
            docs = res.get("documents", [[]])[0]
            ids = res.get("ids", [[]])[0]
            dists = res.get("distances", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            all_docs.extend(docs)
            all_ids.extend(ids)
            all_dists.extend(dists)
            all_metas.extend(metas)
        
        items = sorted(zip(all_docs, all_ids, all_dists, all_metas), key=lambda t: t[2])
        items = items[:k]
        
        if not items:
            return {
                "documents": [[]],
                "ids": [[]],
                "distances": [[]],
                "metadatas": [[]]
            }
        
        docs, ids, dists, metas = zip(*items)
        return {
            "documents": [list(docs)],
            "ids": [list(ids)],
            "distances": [list(dists)],
            "metadatas": [list(metas)]
        }