"""
Tests for Agent classes
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


class TestPlannerAgent:
    @pytest.mark.asyncio
    async def test_default_plan(self):
        from backend.app.agents.planner_agent import PlannerAgent
        planner = PlannerAgent()
        plan = planner._default_plan("What is the revenue for Q3?")
        assert plan["intent"] == "question_answering"
        assert "sub_queries" in plan
        assert plan["top_k"] >= 1

    @pytest.mark.asyncio
    async def test_plan_returns_dict(self):
        from backend.app.agents.planner_agent import PlannerAgent
        planner = PlannerAgent()
        # Without API key, should fall back to default plan
        with patch("anthropic.AsyncAnthropic") as mock_client:
            mock_client.side_effect = Exception("No API key")
            plan = await planner.plan("test query", {})
        assert isinstance(plan, dict)
        assert "strategy" in plan


class TestCriticAgent:
    @pytest.mark.asyncio
    async def test_empty_chunks_returns_insufficient(self):
        from backend.app.agents.critic_agent import CriticAgent
        critic = CriticAgent()
        result = await critic.evaluate("What is X?", [], [])
        assert result["verdict"] == "insufficient"
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_with_chunks_returns_verdict(self):
        from backend.app.agents.critic_agent import CriticAgent
        critic = CriticAgent()
        chunks = [{"text": "X is a framework for building AI applications.", "score": 0.9}]
        with patch("anthropic.AsyncAnthropic") as mock_client:
            mock_client.side_effect = Exception("No API key")
            result = await critic.evaluate("What is X?", chunks)
        assert result["verdict"] in ("sufficient", "insufficient", "partial")


class TestCoordinatorAgent:
    @pytest.mark.asyncio
    async def test_run_returns_answer(self):
        from backend.app.agents.coordinator_agent import CoordinatorAgent

        mock_db = MagicMock()
        coordinator = CoordinatorAgent(db=mock_db)

        # Mock all sub-agents
        coordinator.planner.plan = AsyncMock(return_value={"intent": "qa", "top_k": 3, "needs_web_search": False, "needs_vision": False, "strategy": "rag_only", "sub_queries": ["test"]})
        coordinator.retriever.retrieve = AsyncMock(return_value=[{"text": "Test content", "score": 0.9, "document_id": "doc1", "modality": "text"}])
        coordinator.vision.process_chunks = AsyncMock(return_value=[])
        coordinator.web_search.search = AsyncMock(return_value=[])
        coordinator.memory.load = AsyncMock(return_value={})
        coordinator.memory.save = AsyncMock()
        coordinator.critic.evaluate = AsyncMock(return_value={"verdict": "sufficient", "confidence": 0.9})
        coordinator.answer.generate = AsyncMock(return_value={"answer": "Test answer", "sources": [], "citations": []})

        result = await coordinator.run(
            query="What is the test?",
            session_id="test-session",
            document_ids=["doc1"],
        )

        assert "answer" in result
        assert result["answer"] == "Test answer"
        assert "agent_steps" in result
        assert len(result["agent_steps"]) > 0


class TestMemoryAgent:
    @pytest.mark.asyncio
    async def test_load_returns_context(self):
        from backend.app.agents.memory_agent import MemoryAgent
        memory = MemoryAgent()
        ctx = await memory.load("session-1", [{"role": "user", "content": "Hello"}])
        assert "session_id" in ctx
        assert ctx["session_id"] == "session-1"

    @pytest.mark.asyncio
    async def test_save_does_not_raise(self):
        from backend.app.agents.memory_agent import MemoryAgent
        memory = MemoryAgent()
        # Should not raise even if Redis is down
        await memory.save("session-1", "query", "answer")
