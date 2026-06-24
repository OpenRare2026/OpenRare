from services.skill_base import Skill, SkillContext, SkillResult
from services.rag_service import ChatReference


class LiteratureSearchSkill(Skill):
    name = "literature_search"
    description = "遗传学文献检索 - 搜索本地病例文档和RAG知识库获取相关文献和病例报告"
    skill_type = "tool_call"
    icon = "book"
    input_schema = {
        "query": "str - 搜索关键词",
        "document_types": "list - 文档类型过滤 (patient_summary, variant_report, clinical_notes)"
    }

    def execute(self, context: SkillContext) -> SkillResult:
        if not context.db_session:
            return SkillResult(
                content="Literature search requires database access.",
                references=[],
                confidence=0.0,
                metadata={"error": "no_db_session"}
            )

        documents = self._search_documents(context)
        vector_results = self._search_vectors(context)

        all_results = documents + vector_results
        content = self._format_results(all_results, context.query)
        references = self._build_references(all_results)

        return SkillResult(
            content=content,
            references=references,
            confidence=0.7 if all_results else 0.3,
            metadata={"skill": self.name, "results_count": len(all_results)}
        )

    def _search_documents(self, context: SkillContext) -> list:
        from database.case_models import CaseDocument
        db = context.db_session
        results = []

        try:
            docs = db.query(CaseDocument).filter(
                CaseDocument.patient_id == context.patient_id
            ).limit(10).all()

            for doc in docs:
                if context.query.lower() in doc.content.lower() or context.query.lower() in doc.title.lower():
                    results.append({
                        "id": doc.id,
                        "title": doc.title,
                        "type": doc.document_type,
                        "content": doc.content[:500],
                        "source": "local_db"
                    })
        except Exception:
            pass

        return results

    def _search_vectors(self, context: SkillContext) -> list:
        results = []
        try:
            from services.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            search_results = embedding_service.search(query=context.query, k=5)
            for r in search_results:
                results.append({
                    "id": r.document_id,
                    "title": f"Document {r.document_id}",
                    "type": "vector_search",
                    "content": r.content[:500],
                    "score": r.score,
                    "source": "vector_db"
                })
        except Exception:
            pass

        return results

    def _format_results(self, results: list, query: str) -> str:
        if not results:
            return f"No relevant documents found for query: '{query}'. Try indexing patient documents first."

        parts = [f"**Literature Search Results** ({len(results)} found)\n"]

        for i, r in enumerate(results, 1):
            parts.append(f"**{i}. {r.get('title', 'Untitled')}**")
            parts.append(f"   Type: {r.get('type', 'unknown')} | Source: {r.get('source', 'unknown')}")
            if r.get('score'):
                parts.append(f"   Relevance Score: {r.get('score'):.3f}")
            parts.append(f"   {r.get('content', '')[:200]}...")
            parts.append("")

        return "\n".join(parts)

    def _build_references(self, results: list):
        refs = []
        for r in results[:5]:
            refs.append(ChatReference(
                reference_id=str(r.get("id", "")),
                reference_type=r.get("type", "document"),
                label=r.get("title", "Document")[:50]
            ))
        return refs
