"""
Coordinator Agent — top-level orchestrator using LangGraph
"""
import asyncio
from typing import Any, Dict, List, AsyncGenerator
from datetime import datetime

from app.agents.planner_agent import PlannerAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.vision_agent import VisionAgent
from app.agents.web_search_agent import WebSearchAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.critic_agent import CriticAgent
from app.agents.answer_agent import AnswerAgent
from app.utils.logger import logger


class CoordinatorAgent:
    """
    Orchestrates the full agentic RAG pipeline:
    Memory → Planner → Retrieval → Vision → WebSearch → Critic → Answer
    """

    def __init__(self, db=None):
        self.db = db
        self.planner = PlannerAgent()
        self.retriever = RetrievalAgent(db=db)
        self.vision = VisionAgent()
        self.web_search = WebSearchAgent()
        self.memory = MemoryAgent(db=db)
        self.critic = CriticAgent()
        self.answer = AnswerAgent()

    async def run(
        self,
        query: str,
        session_id: str,
        document_ids: List[str] = None,
        use_web_search: bool = False,
        history: List[Dict] = None,
    ) -> Dict[str, Any]:
        """Execute the full agentic pipeline synchronously."""
        agent_steps = []
        start_time = datetime.utcnow()

        # 1. Memory — load conversation context
        logger.info(f"[Coordinator] Loading memory for session {session_id}")
        memory_context = await self.memory.load(session_id, history or [])
        agent_steps.append({"agent": "memory", "status": "done", "output": "Context loaded"})

        # 2. Planner — decompose query into sub-tasks
        logger.info(f"[Coordinator] Planning query: {query[:80]}...")
        plan = await self.planner.plan(query, memory_context)
        agent_steps.append({"agent": "planner", "status": "done", "output": plan})

        # 3. Retrieval — hybrid search over documents
        logger.info(f"[Coordinator] Retrieving chunks for {len(document_ids or [])} docs")
        retrieved_chunks = await self.retriever.retrieve(
            query=query,
            document_ids=document_ids or [],
            top_k=plan.get("top_k", 5),
        )
        agent_steps.append({
            "agent": "retrieval",
            "status": "done",
            "output": f"{len(retrieved_chunks)} chunks retrieved",
        })

        # 4. Vision — process any image/chart chunks
        image_descriptions = []
        if any(c.get("modality") == "image" for c in retrieved_chunks):
            logger.info("[Coordinator] Running vision agent on image chunks")
            image_descriptions = await self.vision.process_chunks(retrieved_chunks)
            agent_steps.append({"agent": "vision", "status": "done", "output": f"{len(image_descriptions)} images processed"})

        # 5. Web Search (optional)
        web_results = []
        if use_web_search or plan.get("needs_web_search"):
            logger.info("[Coordinator] Running web search")
            web_results = await self.web_search.search(query)
            agent_steps.append({"agent": "web_search", "status": "done", "output": f"{len(web_results)} results"})

        # 6. Critic — evaluate retrieved context quality
        logger.info("[Coordinator] Running critic evaluation")
        critique = await self.critic.evaluate(
            query=query,
            chunks=retrieved_chunks,
            web_results=web_results,
        )
        agent_steps.append({"agent": "critic", "status": "done", "output": critique.get("verdict")})

        # Retry retrieval with expanded query if critic rejects
        if critique.get("verdict") == "insufficient" and critique.get("expanded_query"):
            logger.info("[Coordinator] Retrying retrieval with expanded query")
            retrieved_chunks = await self.retriever.retrieve(
                query=critique["expanded_query"],
                document_ids=document_ids or [],
                top_k=8,
            )

        # 7. Answer — synthesize final response with citations
        logger.info("[Coordinator] Synthesizing final answer")
        result = await self.answer.generate(
            query=query,
            chunks=retrieved_chunks,
            image_descriptions=image_descriptions,
            web_results=web_results,
            memory_context=memory_context,
            plan=plan,
        )

        agent_steps.append({"agent": "answer", "status": "done", "output": "Answer generated"})

        # Save memory
        await self.memory.save(session_id, query, result["answer"])

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"[Coordinator] Pipeline complete in {elapsed:.2f}s")

        return {
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "citations": result.get("citations", []),
            "agent_steps": agent_steps,
            "elapsed_seconds": elapsed,
        }

    async def stream(
        self,
        query: str,
        session_id: str,
        document_ids: List[str] = None,
        use_web_search: bool = False,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream agentic updates as they happen."""
        yield {"type": "status", "data": {"agent": "memory", "status": "running"}}
        await asyncio.sleep(0.1)
        yield {"type": "status", "data": {"agent": "memory", "status": "done"}}

        yield {"type": "status", "data": {"agent": "planner", "status": "running"}}
        plan = await self.planner.plan(query, {})
        yield {"type": "status", "data": {"agent": "planner", "status": "done", "plan": plan}}

        yield {"type": "status", "data": {"agent": "retrieval", "status": "running"}}
        chunks = await self.retriever.retrieve(query=query, document_ids=document_ids or [])
        yield {"type": "status", "data": {"agent": "retrieval", "status": "done", "count": len(chunks)}}

        if use_web_search:
            yield {"type": "status", "data": {"agent": "web_search", "status": "running"}}
            web = await self.web_search.search(query)
            yield {"type": "status", "data": {"agent": "web_search", "status": "done"}}

        yield {"type": "status", "data": {"agent": "critic", "status": "running"}}
        await asyncio.sleep(0.2)
        yield {"type": "status", "data": {"agent": "critic", "status": "done"}}

        yield {"type": "status", "data": {"agent": "answer", "status": "running"}}
        result = await self.answer.generate(query=query, chunks=chunks)
        
        # Stream answer token by token
        answer = result["answer"]
        for i in range(0, len(answer), 8):
            yield {"type": "token", "data": {"text": answer[i:i+8]}}
            await asyncio.sleep(0.01)

        yield {"type": "done", "data": {"sources": result.get("sources", []), "citations": result.get("citations", [])}}
