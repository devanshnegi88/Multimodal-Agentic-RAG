"""
Retrieval Graph — LangGraph sub-graph for the retrieval pipeline
"""
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END


class RetrievalState(TypedDict):
    query: str
    document_ids: List[str]
    top_k: int
    use_hybrid: bool
    chunks: List[Dict[str, Any]]
    reranked_chunks: List[Dict[str, Any]]
    error: Optional[str]


def create_retrieval_graph():
    """Build the retrieval sub-graph with optional reranking."""
    from app.rag.retriever import VectorRetriever
    from app.rag.hybrid_search import HybridSearcher
    from app.rag.reranker import Reranker

    vector_retriever = VectorRetriever()
    hybrid_searcher = HybridSearcher()
    reranker = Reranker()

    async def dense_retrieve(state: RetrievalState) -> RetrievalState:
        if state["use_hybrid"]:
            chunks = await hybrid_searcher.search(
                query=state["query"],
                document_ids=state["document_ids"],
                top_k=state["top_k"] * 2,
            )
        else:
            chunks = await vector_retriever.search(
                query=state["query"],
                document_ids=state["document_ids"],
                top_k=state["top_k"] * 2,
            )
        return {**state, "chunks": chunks}

    async def rerank_node(state: RetrievalState) -> RetrievalState:
        if not state["chunks"]:
            return {**state, "reranked_chunks": []}
        reranked = await reranker.rerank(state["query"], state["chunks"], top_k=state["top_k"])
        return {**state, "reranked_chunks": reranked}

    workflow = StateGraph(RetrievalState)
    workflow.add_node("retrieve", dense_retrieve)
    workflow.add_node("rerank", rerank_node)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "rerank")
    workflow.add_edge("rerank", END)

    return workflow.compile()
