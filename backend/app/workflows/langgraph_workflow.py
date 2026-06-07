"""
LangGraph Workflow — state machine for the full RAG pipeline
"""
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END


class RAGState(TypedDict):
    query: str
    session_id: str
    document_ids: List[str]
    use_web_search: bool
    plan: Optional[Dict[str, Any]]
    retrieved_chunks: List[Dict[str, Any]]
    image_descriptions: List[Dict[str, Any]]
    web_results: List[Dict[str, Any]]
    critique: Optional[Dict[str, Any]]
    answer: Optional[str]
    citations: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    agent_steps: List[Dict[str, Any]]
    retry_count: int
    error: Optional[str]


def create_rag_graph():
    """Build the LangGraph state machine for the RAG pipeline."""
    from app.agents.planner_agent import PlannerAgent
    from app.agents.retrieval_agent import RetrievalAgent
    from app.agents.vision_agent import VisionAgent
    from app.agents.web_search_agent import WebSearchAgent
    from app.agents.critic_agent import CriticAgent
    from app.agents.answer_agent import AnswerAgent

    planner = PlannerAgent()
    retriever = RetrievalAgent()
    vision = VisionAgent()
    web_agent = WebSearchAgent()
    critic = CriticAgent()
    answer_agent = AnswerAgent()

    async def plan_node(state: RAGState) -> RAGState:
        plan = await planner.plan(state["query"], {})
        steps = state["agent_steps"] + [{"agent": "planner", "status": "done"}]
        return {**state, "plan": plan, "agent_steps": steps}

    async def retrieve_node(state: RAGState) -> RAGState:
        chunks = await retriever.retrieve(
            query=state["query"],
            document_ids=state["document_ids"],
            top_k=state.get("plan", {}).get("top_k", 5),
        )
        steps = state["agent_steps"] + [{"agent": "retrieval", "status": "done", "count": len(chunks)}]
        return {**state, "retrieved_chunks": chunks, "agent_steps": steps}

    async def vision_node(state: RAGState) -> RAGState:
        if not state.get("plan", {}).get("needs_vision"):
            return state
        descs = await vision.process_chunks(state["retrieved_chunks"])
        return {**state, "image_descriptions": descs}

    async def web_search_node(state: RAGState) -> RAGState:
        plan = state.get("plan", {})
        if not (state["use_web_search"] or plan.get("needs_web_search")):
            return state
        results = await web_agent.search(state["query"])
        steps = state["agent_steps"] + [{"agent": "web_search", "status": "done"}]
        return {**state, "web_results": results, "agent_steps": steps}

    async def critic_node(state: RAGState) -> RAGState:
        critique = await critic.evaluate(
            query=state["query"],
            chunks=state["retrieved_chunks"],
            web_results=state["web_results"],
        )
        steps = state["agent_steps"] + [{"agent": "critic", "status": "done", "verdict": critique.get("verdict")}]
        return {**state, "critique": critique, "agent_steps": steps}

    async def answer_node(state: RAGState) -> RAGState:
        result = await answer_agent.generate(
            query=state["query"],
            chunks=state["retrieved_chunks"],
            image_descriptions=state["image_descriptions"],
            web_results=state["web_results"],
        )
        steps = state["agent_steps"] + [{"agent": "answer", "status": "done"}]
        return {
            **state,
            "answer": result["answer"],
            "citations": result.get("citations", []),
            "sources": result.get("sources", []),
            "agent_steps": steps,
        }

    def should_retry(state: RAGState) -> str:
        critique = state.get("critique", {})
        retry_count = state.get("retry_count", 0)
        if critique.get("verdict") == "insufficient" and retry_count < 1:
            return "retrieve"
        return "answer"

    # Build the graph
    workflow = StateGraph(RAGState)
    workflow.add_node("plan", plan_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("vision", vision_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("answer", answer_node)

    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "retrieve")
    workflow.add_edge("retrieve", "vision")
    workflow.add_edge("vision", "web_search")
    workflow.add_edge("web_search", "critic")
    workflow.add_conditional_edges("critic", should_retry, {"retrieve": "retrieve", "answer": "answer"})
    workflow.add_edge("answer", END)

    return workflow.compile()


# Singleton compiled graph
_graph = None


def get_rag_graph():
    global _graph
    if _graph is None:
        _graph = create_rag_graph()
    return _graph
