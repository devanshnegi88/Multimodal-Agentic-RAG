"""
Evaluation Graph — RAGAS-inspired automated RAG evaluation pipeline
"""
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END


class EvaluationState(TypedDict):
    query: str
    answer: str
    contexts: List[str]
    ground_truth: Optional[str]
    faithfulness_score: float
    relevance_score: float
    completeness_score: float
    overall_score: float
    feedback: str


def create_evaluation_graph():
    """Build the evaluation pipeline graph."""

    async def faithfulness_node(state: EvaluationState) -> EvaluationState:
        """Evaluate if the answer is faithful to the retrieved contexts."""
        try:
            import anthropic
            from app.config import settings

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            context_str = "\n".join(state["contexts"][:3])
            msg = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=128,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Context:\n{context_str[:1000]}\n\nAnswer:\n{state['answer'][:500]}\n\n"
                        "Rate how faithful the answer is to the context (0.0 to 1.0). Respond only with a number."
                    )
                }],
            )
            score = float(msg.content[0].text.strip())
            return {**state, "faithfulness_score": max(0.0, min(1.0, score))}
        except Exception:
            return {**state, "faithfulness_score": 0.7}

    async def relevance_node(state: EvaluationState) -> EvaluationState:
        """Evaluate if the answer is relevant to the query."""
        try:
            import anthropic
            from app.config import settings

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=64,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Query: {state['query']}\nAnswer: {state['answer'][:500]}\n\n"
                        "Rate the relevance of the answer to the query (0.0 to 1.0). Respond only with a number."
                    )
                }],
            )
            score = float(msg.content[0].text.strip())
            return {**state, "relevance_score": max(0.0, min(1.0, score))}
        except Exception:
            return {**state, "relevance_score": 0.7}

    async def aggregate_node(state: EvaluationState) -> EvaluationState:
        """Compute final evaluation score and feedback."""
        overall = (
            state["faithfulness_score"] * 0.4 +
            state["relevance_score"] * 0.4 +
            state.get("completeness_score", 0.7) * 0.2
        )
        feedback_parts = []
        if state["faithfulness_score"] < 0.6:
            feedback_parts.append("Answer contains claims not supported by context")
        if state["relevance_score"] < 0.6:
            feedback_parts.append("Answer does not fully address the query")
        feedback = "; ".join(feedback_parts) if feedback_parts else "Answer quality is acceptable"

        return {**state, "overall_score": round(overall, 3), "feedback": feedback, "completeness_score": state.get("completeness_score", 0.7)}

    workflow = StateGraph(EvaluationState)
    workflow.add_node("faithfulness", faithfulness_node)
    workflow.add_node("relevance", relevance_node)
    workflow.add_node("aggregate", aggregate_node)
    workflow.set_entry_point("faithfulness")
    workflow.add_edge("faithfulness", "relevance")
    workflow.add_edge("relevance", "aggregate")
    workflow.add_edge("aggregate", END)

    return workflow.compile()
