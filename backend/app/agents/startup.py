"""Agent Startup Wiring — Instantiates all 13 agents and registers them on server boot.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 6
Called from: main.py lifespan (startup)

This module is the single place where all 13 agents are created,
configured, and registered with the AgentRegistry singleton.

Full Agent Mesh (Architecture V3):
  Planning:  RAG(1), Clarification(2), WebSearch(3), SPA(4), SAA(5)
  Execution: EA(6), Observer(7)
  Safety:    Safety(8)
  Support:   UserAgent(9), CMA(10), Orchestrator(11), AppRegistry(12), WorkflowLearning(13)
"""

from __future__ import annotations

from app.agents.registry import agent_registry
from app.core.logging_config import get_logger
from app.services.ollama_service import OllamaService
from app.services.desktop_automation import DesktopAutomationService
from app.services.voice_service import voice_service as voice_svc

logger = get_logger(__name__)


async def register_all_agents() -> None:
    """Create and register all 13 agents with the singleton registry.

    Called once during FastAPI lifespan startup.
    """
    # ── Shared services (injected into agents that need them) ──
    ollama = OllamaService()
    desktop = DesktopAutomationService()

    # ── Agent 1: RAG Agent (Planning — intent → plan) ─────────
    from app.agents.rag_agent import RAGAgent
    rag = RAGAgent(ollama_service=ollama)
    agent_registry.register_instance(rag, capabilities=["planning", "intent_parsing", "plan_generation"])

    # ── Agent 2: Clarification Agent (Disambiguator) ──────────
    from app.agents.clarification_agent import ClarificationAgent
    clarification = ClarificationAgent(ollama_service=ollama)
    agent_registry.register_instance(clarification, capabilities=["clarification", "disambiguation"])

    # ── Agent 3: Web Search Agent (Fact finder) ───────────────
    from app.agents.web_search_agent import WebSearchAgent
    web_search = WebSearchAgent()
    agent_registry.register_instance(web_search, capabilities=["web_search", "knowledge"])

    # ── Agent 4: SPA — Semantic Plan Annotator ────────────────
    from app.agents.spa_agent import SPAAgent
    spa = SPAAgent(ollama_service=ollama)
    agent_registry.register_instance(spa, capabilities=["annotation", "plan_enrichment"])

    # ── Agent 5: SAA — Step-Action Adapter ────────────────────
    from app.agents.saa_agent import SAAAgent
    saa = SAAAgent(ollama_service=ollama)
    agent_registry.register_instance(saa, capabilities=["action_mapping", "method_selection"])

    # ── Agent 6: Execution Agent (The Hands) ──────────────────
    from app.agents.execution_agent import ExecutionAgent
    ea = ExecutionAgent(desktop_service=desktop)
    agent_registry.register_instance(ea, capabilities=["execution", "desktop_automation"])

    # ── Agent 7: Observer Agent (Verification) ────────────────
    from app.agents.observer_agent import ObserverAgent
    oa = ObserverAgent(desktop_service=desktop)
    agent_registry.register_instance(oa, capabilities=["verification", "observation"])

    # ── Agent 8: Safety Agent (Pre-execution Gate) ────────────
    from app.agents.safety_agent import SafetyAgent
    safety = SafetyAgent(strict_mode=True)
    agent_registry.register_instance(safety, capabilities=["safety", "security_gate"])

    # ── Agent 9: User Agent (Voice/Text I/O Bridge) ──────────
    from app.agents.user_agent import UserAgent
    user_agent = UserAgent(ollama_service=ollama, voice_service=voice_svc)
    agent_registry.register_instance(user_agent, capabilities=["user_io", "voice", "text"])

    # ── Agent 10: CMA — Context Management Agent ─────────────
    from app.agents.cma_agent import CMAAgent
    cma = CMAAgent()
    agent_registry.register_instance(cma, capabilities=["context", "session_memory", "preferences"])

    # ── Agent 12: App Registry Agent (System scanner) ─────────
    from app.agents.app_registry_agent import AppRegistryAgent
    app_reg = AppRegistryAgent()
    agent_registry.register_instance(app_reg, capabilities=["app_discovery", "app_lookup"])

    # ── Agent 13: Workflow Learning Agent ─────────────────────
    from app.agents.workflow_learning_agent import WorkflowLearningAgent
    wf_learner = WorkflowLearningAgent()
    agent_registry.register_instance(wf_learner, capabilities=["workflow_learning", "pattern_reuse"])

    # Note: Agent 11 (Orchestrator) already exists as a separate module
    # and is not registered as a BaseAgent — it dispatches to all other agents.

    # Log summary
    all_agents = agent_registry.list_all()
    logger.info(
        "all_agents_registered",
        count=len(all_agents),
        agents=[a["name"] for a in all_agents],
    )


async def shutdown_agents() -> None:
    """Cleanup on shutdown."""
    await agent_registry.stop_health_monitor()
    logger.info("agents_shutdown_complete")
