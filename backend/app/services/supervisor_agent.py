import asyncio
import concurrent.futures
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.models.document import Document
from app.models.chat import ChatMessage
from app.services.hybrid_search_service import hybrid_search_service
from app.services.vector_service import vector_service
from app.services.llm_service import llm_service, AllProvidersUnavailableError

logger = logging.getLogger(__name__)


def run_async_safe(coro):
    """Safely runs an async coroutine from a synchronous thread."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result(timeout=45)
    else:
        return loop.run_until_complete(coro)


class ResearchTool:
    ACADEMIC_SEARCH = "academic_paper_search"
    PAPER_SUMMARY = "paper_summarization"
    LITERATURE_REVIEW = "literature_review"
    PAPER_COMPARISON = "paper_comparison"
    RESEARCH_GAPS = "research_gap_identification"
    WORKSPACE_QA = "workspace_qa"


TOOL_METADATA = {
    ResearchTool.ACADEMIC_SEARCH: {
        "name": "Academic Paper Search",
        "icon": "🔍",
        "intent": "Literature Discovery & Search",
        "description": "Searches online scientific repositories (arXiv, PubMed, Semantic Scholar, IEEE, ACM) for academic papers.",
    },
    ResearchTool.PAPER_SUMMARY: {
        "name": "Paper Summarization",
        "icon": "📄",
        "intent": "Paper Summarization",
        "description": "Extracts objectives, methodology, key findings, and contributions from an academic paper.",
    },
    ResearchTool.LITERATURE_REVIEW: {
        "name": "Literature Review",
        "icon": "📚",
        "intent": "Literature Synthesis & Review",
        "description": "Synthesizes multiple papers into an evidence-grounded thematic literature review.",
    },
    ResearchTool.PAPER_COMPARISON: {
        "name": "Paper Comparison",
        "icon": "⚖️",
        "intent": "Comparative Literature Analysis",
        "description": "Constructs a comparative matrix evaluating datasets, models, metrics, and results across papers.",
    },
    ResearchTool.RESEARCH_GAPS: {
        "name": "Research Gap Identification",
        "icon": "🎯",
        "intent": "Research Gap & Limitation Analysis",
        "description": "Uncovers unaddressed challenges, methodological shortcomings, and open future research directions.",
    },
    ResearchTool.WORKSPACE_QA: {
        "name": "Workspace RAG Q&A",
        "icon": "💬",
        "intent": "Workspace Document Question Answering",
        "description": "Retrieves semantic vector context from workspace documents to answer factual research queries.",
    },
}


class ResearchSupervisorAgent:
    """
    Research Supervisor Agent
    - Accepts user's research queries.
    - Understands user's intention.
    - Decides which research tool to use.
    - Invokes the appropriate research tool automatically.
    - Synthesizes the final grounded response with execution trace.
    """

    def __init__(self):
        self.tools = TOOL_METADATA

    def _extract_search_keyword(self, query: str) -> str:
        """Strips conversational prefixes to extract clean academic search terms."""
        cleaned = re.sub(
            r"^(?:please\s+|can\s+you\s+|could\s+you\s+|i\s+want\s+to\s+|help\s+me\s+)?(?:search(?:\s+for)?|find|look(?:\s+up)?|discover|fetch|get)\s+(?:recent\s+|latest\s+|new\s+|relevant\s+|top\s+)?(?:academic\s+|scientific\s+)?(?:papers?|articles?|literature|research|publications?)(?:\s+(?:on|about|regarding|for|in))?\s*",
            "",
            query,
            flags=re.IGNORECASE,
        ).strip()
        cleaned = re.sub(r"^(?:papers?\s+(?:on|about|regarding|for))\s*", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = cleaned.rstrip("?.!,;:")
        return cleaned if len(cleaned) >= 3 else query.strip()

    def _extract_target_paper_title(self, query: str, papers: List[Paper]) -> Optional[Paper]:
        """Tries to match a specific paper mentioned in the query."""
        if not papers:
            return None

        # 1. Quoted title check ('title' or "title")
        quoted_matches = re.findall(r"['\"]([^'\"]{4,})['\"]", query)
        for quoted in quoted_matches:
            quoted_norm = quoted.lower().strip()
            for p in papers:
                if not p.title:
                    continue
                p_norm = p.title.lower().strip()
                if quoted_norm == p_norm or quoted_norm in p_norm or p_norm in quoted_norm:
                    return p

        q_lower = query.lower()

        # 2. Direct title inclusion check
        for p in papers:
            if p.title and p.title.lower() in q_lower:
                return p

        # 3. Clean alphanumeric match (ignoring punctuation)
        clean_q = re.sub(r"[^\w\s]", " ", q_lower)
        clean_q_compact = re.sub(r"\s+", " ", clean_q).strip()
        for p in papers:
            if not p.title:
                continue
            clean_p = re.sub(r"[^\w\s]", " ", p.title.lower())
            clean_p_compact = re.sub(r"\s+", " ", clean_p).strip()
            if clean_p_compact and (clean_p_compact in clean_q_compact or clean_q_compact in clean_p_compact):
                return p

        # 4. Significant word overlap check
        best_paper = None
        best_overlap = 0
        q_words = set(re.findall(r"\w+", q_lower))
        stop_words = {"the", "a", "an", "and", "or", "in", "on", "for", "with", "about", "paper", "summarize", "summary", "review", "workspace", "my"}
        q_content_words = q_words - stop_words

        for p in papers:
            if not p.title:
                continue
            p_words = set(re.findall(r"\w+", p.title.lower())) - stop_words
            overlap = len(q_content_words & p_words)
            if overlap > best_overlap and overlap >= 2:
                best_overlap = overlap
                best_paper = p

        return best_paper or papers[0]

    def _classify_intent(
        self,
        query: str,
        papers_count: int,
        paper_ids: List[int],
    ) -> Tuple[str, str]:
        """
        Understands the user's research intention and selects the appropriate tool.
        Priority:
        1. Paper Comparison (Contrasting multiple papers)
        2. Literature Review (Thematic synthesis across multiple papers)
        3. Paper Summarization (Explicit summarize/summary requests; the word "limitations" alone does not override summarization)
        4. Research Gap Identification (Explicitly asks to identify, find, or analyze research gaps or limitations)
        5. Academic Paper Search (Explicit literature search actions only)
        6. Workspace Q&A (Default semantic vector Q&A)
        """
        normalized = query.lower().strip()

        # 1. Paper Comparison (Contrasting multiple papers)
        compare_patterns = [
            r"\bcompare\b",
            r"\bcomparison\b",
            r"\bdifference\s+between\b",
            r"\bversus\b",
            r"\bvs\.?\b",
            r"\bcontrast\b",
            r"\bbenchmark\s+against\b",
            r"\bcomparative\s+matrix\b",
            r"\bside\s+by\s+side\b",
            r"\bhow\s+do\s+(?:these|the)\s+papers\s+differ\b",
        ]
        if any(re.search(pat, normalized) for pat in compare_patterns) or (len(paper_ids) >= 2 and "compare" in normalized):
            return (
                ResearchTool.PAPER_COMPARISON,
                "User requested comparative analysis contrasting multiple methodologies, models, or empirical results."
            )

        # 2. Literature Review (Thematic synthesis across papers)
        lit_review_patterns = [
            r"\bliterature\s+review\b",
            r"\blit\s+review\b",
            r"\bsynthesize\s+(?:the\s+|these\s+)?papers\b",
            r"\bstate\s+of\s+the\s+art\s+review\b",
            r"\bsota\s+review\b",
            r"\bthematic\s+review\b",
            r"\bsurvey\s+of\s+(?:our|the|collected)\s+(?:papers|literature)\b",
            r"\bsurvey\s+of\s+literature\b",
        ]
        if any(re.search(pat, normalized) for pat in lit_review_patterns):
            return (
                ResearchTool.LITERATURE_REVIEW,
                "User requested a multi-paper literature synthesis outlining common themes, agreements, and debates."
            )

        # 3. Paper Summarization (Explicit summarize/summary requests)
        # Rule 1: Explicit summarize/summary requests must select Paper Summarization.
        # Rule 3: Do not let the word "limitations" alone override an explicit summarization request.
        summary_patterns = [
            r"\bsummarize\b",
            r"\bsummarise\b",
            r"\bsummary\b",
            r"\bgive\s+(?:me\s+)?(?:a\s+)?summary\b",
            r"\bprovide\s+(?:a\s+)?summary\b",
            r"\bbrief\s+(?:of|overview)\b",
            r"\btl;?dr\b",
            r"\bcondense\b",
            r"\babstract\s+of\s+(?:this|the)\s+paper\b",
            r"\bkey\s+contributions\s+of\b",
            r"\bmain\s+findings\s+of\b",
        ]
        if any(re.search(pat, normalized) for pat in summary_patterns):
            return (
                ResearchTool.PAPER_SUMMARY,
                "User explicitly requested a structured academic summary of paper objective, methodology, key findings, and limitations."
            )

        # 4. Research Gap Identification
        # Rule 2: Research gap identification should trigger when the user explicitly asks to identify, find, or analyze research gaps or limitations.
        gap_patterns = [
            r"\b(?:identify|find|analyze|analyse|detect|uncover|investigate|explore|extract|list|show)\s+(?:the\s+)?(?:research\s+)?(?:gaps?|limitations?)\b",
            r"\b(?:what\s+are|what're)\s+(?:the\s+)?(?:research\s+)?(?:gaps?|limitations?)\b",
            r"\bresearch\s+gaps?\b",
            r"\bgaps?\s+in\b",
            r"\blimitations?\s+(?:in|of|across)\b",
            r"\bmethodological\s+limitations?\b",
            r"\bunaddressed\b",
            r"\bunexplored\b",
            r"\bopen\s+(?:research\s+)?(?:challenges?|questions?)\b",
            r"\bfuture\s+(?:research\s+)?directions?\b",
            r"\bfuture\s+work\s+across\b",
            r"\bmissing\s+in\s+(?:the\s+)?literature\b",
            r"\bweaknesses?\s+across\b",
        ]
        if any(re.search(pat, normalized) for pat in gap_patterns):
            return (
                ResearchTool.RESEARCH_GAPS,
                "Query focuses on identifying critical scientific limitations, unexplored areas, and open research gaps across the literature."
            )

        # 5. Academic Paper Search (Explicit Search Actions Only - Priority 5)
        search_patterns = [
            r"\bsearch\s+(?:for\s+)?(?:recent\s+|latest\s+|new\s+|relevant\s+)?(?:academic\s+|scientific\s+)?papers?\b",
            r"\bfind\s+(?:recent\s+|latest\s+|new\s+|relevant\s+)?(?:academic\s+|scientific\s+)?papers?\b",
            r"\blook\s+(?:up|for)\s+(?:recent\s+|latest\s+|new\s+|relevant\s+)?(?:academic\s+|scientific\s+)?papers?\b",
            r"\bdiscover\s+(?:recent\s+|latest\s+|new\s+|relevant\s+)?papers?\b",
            r"\bsearch\s+(?:arxiv|pubmed|semantic\s+scholar|ieee|acm)\b",
            r"\bfind\s+(?:academic\s+)?(?:literature|research)\s+(?:on|about|for)\b",
            r"\bfetch\s+papers?\b",
            r"\bget\s+papers?\b",
            r"^(?:search|find|lookup)\s+",
            r"^papers\s+(?:on|about)\s+",
        ]
        if any(re.search(pat, normalized) for pat in search_patterns):
            return (
                ResearchTool.ACADEMIC_SEARCH,
                "Query expresses explicit intent to discover and search external academic literature on the specified topic."
            )

        # 6. Default: Workspace Q&A with vector RAG
        return (
            ResearchTool.WORKSPACE_QA,
            "Query represents a specific conceptual or factual research question regarding workspace literature."
        )

    def _execute_academic_search(self, query: str) -> str:
        search_term = self._extract_search_keyword(query)
        try:
            papers = run_async_safe(hybrid_search_service.search(query=search_term, max_results=5))
        except Exception as e:
            logger.error("Academic search tool failed: %s", e)
            papers = []

        if not papers:
            return (
                f"### Academic Repository Search Results\n\n"
                f"No papers were directly returned for query: **\"{search_term}\"**.\n\n"
                f"- Please check spelling or broaden search keywords.\n"
                f"- You can also use the **Search Papers** tab in the sidebar to search specific repositories."
            )

        output = [
            f"### Academic Literature Search: *\"{search_term}\"*\n",
            f"Discovered **{len(papers)}** relevant peer-reviewed publication(s) across academic repositories (arXiv, PubMed, Semantic Scholar, etc.):\n"
        ]

        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "Untitled")
            authors_list = paper.get("authors") or []
            if isinstance(authors_list, list):
                authors = ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else "")
            else:
                authors = str(authors_list)
            year = paper.get("published_date") or paper.get("year") or "N/A"
            source = paper.get("source", "Academic Index")
            url = paper.get("preferred_access_url") or paper.get("paper_url") or paper.get("pdf_url") or ""
            abstract = paper.get("abstract") or "No abstract summary available."
            abstract_snippet = abstract[:280] + "..." if len(abstract) > 280 else abstract

            output.append(f"#### {i}. {title}")
            output.append(f"- **Authors:** {authors or 'Not specified'}")
            output.append(f"- **Venue/Source:** `{source}` | **Date:** {year}")
            if url:
                output.append(f"- **Direct Paper Access:** [{url}]({url})")
            output.append(f"- **Summary Abstract:** {abstract_snippet}\n")

        output.append(
            "\n> 💡 **Next Steps:** You can import any of these publications into your active workspace "
            "using the **Search Papers** page to enable in-depth Q&A, full-text extraction, and comparative analysis."
        )
        return "\n".join(output)

    def _build_paper_payload(self, paper: Paper, workspace_id: int, query_type: str = "summary") -> Dict[str, Any]:
        evidence_pack = vector_service.build_evidence_pack(
            paper_id=paper.id,
            workspace_id=workspace_id,
            title=paper.title,
            query="objective methodology dataset model architecture evaluation metrics results conclusion contributions limitations future work",
            limit=8,
        )
        indexed_chunks = [c.get("content", "") for c in evidence_pack.get("chunks", [])]
        indexed_content = evidence_pack.get("text") or "\n\n".join(indexed_chunks).strip()
        text_content = indexed_content or paper.text_content or paper.abstract or ""
        return {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "text_content": text_content,
            "evidence_chunks": evidence_pack.get("chunks", []),
            "source_priority": "Full PDF text chunks" if indexed_content else ("Abstract" if paper.abstract else "Metadata"),
            "chunk_count_used": len(indexed_chunks) or 1,
            "evidence_confidence": "High" if len(indexed_chunks) >= 4 else "Medium",
            "published_date": paper.published_date,
            "source": paper.source,
        }

    def _execute_summarization(self, query: str, workspace_id: int, papers: List[Paper]) -> str:
        if not papers:
            return (
                "### Paper Summarization Tool\n\n"
                "⚠️ **No papers found in current workspace.**\n\n"
                "To summarize an academic paper:\n"
                "1. Upload a PDF via **Upload PDF**, or\n"
                "2. Import preprints from the **Search Papers** catalog into this workspace.\n\n"
                "You can also ask me to search papers online (e.g., `Search for papers on Transformers`)."
            )

        target_paper = self._extract_target_paper_title(query, papers)
        payload = self._build_paper_payload(target_paper, workspace_id, "summary")

        summary = llm_service.generate_summary(
            title=target_paper.title,
            abstract=target_paper.abstract or "",
            full_text=payload["text_content"],
            paper_id=target_paper.id,
            chunks=payload.get("evidence_chunks"),
            metadata=payload,
        )
        return summary

    def _execute_literature_review(self, workspace_id: int, papers: List[Paper]) -> str:
        if len(papers) < 2:
            paper_info = f"Only 1 paper (*{papers[0].title}*) is currently available." if papers else "No papers are available."
            return (
                "### Literature Review Tool\n\n"
                f"⚠️ **Insufficient workspace papers for a multi-study literature review.**\n\n"
                f"{paper_info}\n\n"
                "A comprehensive literature review synthesizes common themes and debates across at least **two** publications.\n"
                "Please import or upload additional papers into this workspace, or use `Search papers on <topic>` to find more literature."
            )

        papers_data = [self._build_paper_payload(p, workspace_id, "lit_review") for p in papers[:6]]
        return llm_service.generate_literature_review(papers_data)

    def _execute_paper_comparison(self, workspace_id: int, papers: List[Paper]) -> str:
        if len(papers) < 2:
            return (
                "### Paper Comparison Tool\n\n"
                "⚠️ **At least two papers are required in this workspace to construct a comparative matrix.**\n\n"
                "Please upload or import at least two papers into this workspace, then ask me to compare them."
            )

        papers_data = [self._build_paper_payload(p, workspace_id, "comparison") for p in papers[:5]]
        return llm_service.compare_papers(papers_data)

    def _execute_research_gaps(self, workspace_id: int, papers: List[Paper]) -> str:
        if not papers:
            return (
                "### Research Gap Identification Tool\n\n"
                "⚠️ **No research papers found in this workspace.**\n\n"
                "The Research Gap Identification tool analyzes research papers currently in your active workspace to detect methodological limitations, empirical shortcomings, and unaddressed research questions.\n\n"
                "To identify research gaps:\n"
                "1. Upload a research paper PDF via **Upload PDF**, or\n"
                "2. Import publications from the **Search Papers** page into this workspace.\n\n"
                "Once papers are added to the workspace, the Supervisor Agent will ground the research gap analysis in the actual literature."
            )

        papers_data = [self._build_paper_payload(p, workspace_id, "gaps") for p in papers[:6]]
        return llm_service.identify_research_gaps(papers_data)

    def _execute_workspace_qa(
        self,
        query: str,
        workspace_id: int,
        session_id: int,
        user_msg_id: int,
        paper_ids: List[int],
        document_ids: List[int],
        db: Session,
    ) -> str:
        history_objs = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.id != user_msg_id,
        ).order_by(ChatMessage.timestamp.asc()).all()
        chat_history = [{"role": m.role, "content": m.content} for m in history_objs]

        # Retrieve relevant chunks
        if paper_ids:
            chunks = []
            for pid in paper_ids:
                p_chunks = vector_service.get_paper_chunks(pid, workspace_id, limit=4)
                for idx, c in enumerate(p_chunks):
                    chunks.append({"content": c, "metadata": {"paper_id": pid, "chunk_index": idx}, "score": 1.0})
        else:
            chunks = vector_service.search_workspace(workspace_id=workspace_id, query=query, top_k=8)

        active_papers = []
        seen = set()
        for c in chunks:
            pid = c.get("metadata", {}).get("paper_id")
            if pid and pid not in seen:
                seen.add(pid)
                p = db.query(Paper).filter(Paper.id == pid).first()
                if p:
                    active_papers.append({"id": p.id, "title": p.title, "authors": p.authors, "abstract": p.abstract})

        return llm_service.generate_rag_response(
            query=query,
            chunks=chunks,
            chat_history=chat_history,
            active_papers=active_papers,
        )

    def run(
        self,
        db: Session,
        workspace_id: int,
        session_id: int,
        query: str,
        user_msg_id: int,
        paper_ids: List[int] = None,
        document_ids: List[int] = None,
    ) -> str:
        paper_ids = paper_ids or []
        document_ids = document_ids or []

        # 1. Fetch available papers in workspace
        workspace_papers = db.query(Paper).filter(Paper.workspace_id == workspace_id).all()
        if paper_ids:
            selected_papers = [p for p in workspace_papers if p.id in paper_ids]
            if selected_papers:
                workspace_papers = selected_papers

        # 2. Research Supervisor Agent understands user intent and decides tool
        selected_tool_key, reasoning = self._classify_intent(
            query=query,
            papers_count=len(workspace_papers),
            paper_ids=paper_ids,
        )
        tool_info = self.tools[selected_tool_key]

        logger.info(
            "Supervisor Agent: query=%r, selected_tool=%s, reasoning=%s",
            query,
            selected_tool_key,
            reasoning,
        )

        # 3. Basic Tool Calling: Invoke selected tool
        try:
            if selected_tool_key == ResearchTool.ACADEMIC_SEARCH:
                tool_output = self._execute_academic_search(query)
                status_note = "Executed academic query across live repositories."

            elif selected_tool_key == ResearchTool.PAPER_SUMMARY:
                tool_output = self._execute_summarization(query, workspace_id, workspace_papers)
                status_note = "Awaiting papers in workspace." if not workspace_papers else "Analyzed paper context and synthesized structured summary."

            elif selected_tool_key == ResearchTool.LITERATURE_REVIEW:
                tool_output = self._execute_literature_review(workspace_id, workspace_papers)
                status_note = "Insufficient papers in workspace (at least 2 required)." if len(workspace_papers) < 2 else f"Synthesized cross-paper themes across {len(workspace_papers[:6])} papers."

            elif selected_tool_key == ResearchTool.PAPER_COMPARISON:
                tool_output = self._execute_paper_comparison(workspace_id, workspace_papers)
                status_note = "Insufficient papers in workspace (at least 2 required)." if len(workspace_papers) < 2 else f"Constructed comparative matrix for {len(workspace_papers[:5])} papers."

            elif selected_tool_key == ResearchTool.RESEARCH_GAPS:
                tool_output = self._execute_research_gaps(workspace_id, workspace_papers)
                if not workspace_papers:
                    status_note = "Awaiting research papers in workspace."
                else:
                    titles = ", ".join(f'"{p.title}"' for p in workspace_papers[:2])
                    if len(workspace_papers) > 2:
                        titles += f" (+{len(workspace_papers) - 2} more)"
                    status_note = f"Analyzed workspace literature ({titles}) for research gaps and limitations."

            else:  # WORKSPACE_QA
                tool_output = self._execute_workspace_qa(
                    query=query,
                    workspace_id=workspace_id,
                    session_id=session_id,
                    user_msg_id=user_msg_id,
                    paper_ids=paper_ids,
                    document_ids=document_ids,
                    db=db,
                )
                status_note = "Retrieved workspace embeddings for grounded answer."

        except AllProvidersUnavailableError as exc:
            tool_output = (
                "⚠️ **AI Generation Unavailable**: All configured LLM providers (Groq, Gemini, OpenRouter, Ollama) "
                "are currently unreachable or lack an active API key in `.env`.\n\n"
                "Please configure an API key (e.g., `GROQ_API_KEY` or `GEMINI_API_KEY`) in the backend `.env` file."
            )
            status_note = "LLM provider connection failed."
        except Exception as exc:
            logger.exception("Supervisor Agent tool execution error: %s", exc)
            tool_output = f"⚠️ Tool execution encountered an issue: {str(exc)}"
            status_note = "Execution error."

        # 4. Final Response Generation with Supervisor Agent Decision Trace
        agent_banner = (
            f"> 🤖 **Research Supervisor Agent**\n"
            f"> • **Intent Identified:** {tool_info['intent']}\n"
            f"> • **Selected Tool:** {tool_info['icon']} **{tool_info['name']}**\n"
            f"> • **Supervisor Reasoning:** {reasoning}\n"
            f"> • **Execution Status:** {status_note}\n\n"
            f"---\n\n"
        )

        return agent_banner + tool_output


supervisor_agent = ResearchSupervisorAgent()

