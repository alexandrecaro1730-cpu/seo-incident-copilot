from seo_incident_copilot.config import default_config
from seo_incident_copilot.rag.retriever import KnowledgeBaseRetriever


def test_retriever_finds_intent_shift_playbook():
    config = default_config()
    retriever = KnowledgeBaseRetriever(config.data_dir / "knowledge_base")
    results = retriever.retrieve("intent shift listicle comparison review")
    assert results
    assert any("intent_shift" in result["doc_id"] for result in results)
