"""
Business objective:
Ground AI recommendations in approved SEO playbooks instead of letting the model
invent playbooks or client actions.

Coding objective:
Implement a small deterministic keyword retriever over markdown files. This is not
a vector database yet; it is a testable RAG placeholder that can later be swapped
for embeddings or a managed vector store.
"""

from __future__ import annotations

from pathlib import Path


class KnowledgeBaseRetriever:
    """Simple keyword-based retrieval over local markdown playbooks."""

    def __init__(self, knowledge_base_dir: Path) -> None:
        self.knowledge_base_dir = knowledge_base_dir
        self.documents = self._load_documents()

    def _load_documents(self) -> dict[str, str]:
        """Load all markdown documents into memory for deterministic tests."""

        docs: dict[str, str] = {}
        for path in sorted(self.knowledge_base_dir.glob("*.md")):
            docs[path.stem] = path.read_text(encoding="utf-8")
        return docs

    def retrieve(self, query: str, top_k: int = 2) -> list[dict[str, str | int]]:
        """Return the highest-scoring playbook snippets for the query."""

        query_terms = {term.lower().strip(".,:;()[]") for term in query.split() if len(term) > 3}
        scored: list[tuple[int, str, str]] = []
        for doc_id, text in self.documents.items():
            text_lower = text.lower()
            score = sum(1 for term in query_terms if term in text_lower)
            if score:
                scored.append((score, doc_id, text[:800]))

        scored.sort(reverse=True)
        return [
            {"doc_id": doc_id, "score": score, "snippet": snippet}
            for score, doc_id, snippet in scored[:top_k]
        ]
