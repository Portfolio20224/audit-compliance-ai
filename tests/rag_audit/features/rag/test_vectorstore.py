def test_add_and_search_analysis(vectorstore_tmp):
    analysis = {
        "requirement": "REQ-001",
        "verdict": "compliant",
        "score": 95,
        "justification": "All checks passed.",
        "evidence_used": {"file": "report.pdf"},
        "recommendations": ["Continue monitoring"]
    } 

    vectorstore_tmp.add_analysis(analysis)
    result = vectorstore_tmp.search_analysis("REQ-001")

    assert len(result["ids"]) >= 1
    assert "REQ-001" in result["metadatas"][0][0]["requirement"]


def test_update_analysis(vectorstore_tmp):
    analysis = {
        "requirement": "REQ-002",
        "verdict": "non-compliant",
        "score": 40,
        "justification": "Missing evidence",
        "evidence_used": {},
        "recommendations": ["Provide missing documentation"]
    }

    vectorstore_tmp.add_analysis(analysis)

    updated = analysis.copy()
    updated["score"] = 85
    updated["verdict"] = "partially-compliant"

    vectorstore_tmp.add_analysis(updated, update_existing=True)

    result = vectorstore_tmp.search_analysis("REQ-002")
    metadata = result["metadatas"][0][0]

    assert metadata["score"] == 85
    assert metadata["verdict"] == "partially-compliant"


def test_add_evidence(vectorstore_tmp):
    vectorstore_tmp.add_evidence("REQ-003", {"note": "Document checked"})
    result = vectorstore_tmp.search_evidence("Document")

    assert len(result["ids"]) >= 1
    assert "REQ-003" in result["metadatas"][0][0]["requirement"]
