"""交付规划 Agent 工作流模块。"""
from app.agent.state import MovingAgentState
from app.agent.moving_agent.nodes import (
    read_confirmed_configuration,
    generate_delivery_phases,
    generate_phase_tasks,
    generate_site_risks,
    generate_response,
)
import logging

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, END
except Exception:  # pragma: no cover - Demo fallback for environments without LangGraph
    StateGraph = None
    END = None


NODES = [
    read_confirmed_configuration,
    generate_delivery_phases,
    generate_phase_tasks,
    generate_site_risks,
    generate_response,
]


def create_moving_agent_graph():
    """创建交付规划 Agent 工作流图；LangGraph 不可用时返回线性兜底。"""
    if StateGraph is None:
        return None
    graph = StateGraph(MovingAgentState)
    graph.add_node("read_confirmed_configuration", read_confirmed_configuration)
    graph.add_node("generate_delivery_phases", generate_delivery_phases)
    graph.add_node("generate_phase_tasks", generate_phase_tasks)
    graph.add_node("generate_site_risks", generate_site_risks)
    graph.add_node("generate_response", generate_response)
    graph.set_entry_point("read_confirmed_configuration")
    graph.add_edge("read_confirmed_configuration", "generate_delivery_phases")
    graph.add_edge("generate_delivery_phases", "generate_phase_tasks")
    graph.add_edge("generate_phase_tasks", "generate_site_risks")
    graph.add_edge("generate_site_risks", "generate_response")
    graph.add_edge("generate_response", END)
    return graph.compile()


_moving_agent = None


def get_moving_agent():
    global _moving_agent
    if _moving_agent is None:
        _moving_agent = create_moving_agent_graph()
    return _moving_agent


async def _run_linear(initial_state: MovingAgentState) -> MovingAgentState:
    state = initial_state
    for node in NODES:
        state = await node(state)
    return state


async def run_moving_agent(user_id: str, user_message: str, context: dict = None) -> dict:
    logger.info("[交付规划Agent] 开始处理 Demo 请求")
    initial_state: MovingAgentState = {
        "user_id": user_id,
        "user_message": user_message,
        "source_address": None,
        "target_address": None,
        "source_rooms": [],
        "target_rooms": [],
        "moving_date": None,
        "mover_count": None,
        "vehicle_type": None,
        "items": [],
        "boxes": [],
        "estimated_cost": None,
        "cost_breakdown": {},
        "unpacking_guide": [],
        "response": None,
        "generated_checklist": None,
        "suggested_actions": [],
        "error": None,
        "confirmed_configuration": {},
        "delivery_phases": [],
        "site_risks": [],
    }
    if context:
        for key, value in context.items():
            initial_state[key] = value
    agent = get_moving_agent()
    result = await agent.ainvoke(initial_state) if agent else await _run_linear(initial_state)
    logger.info("[交付规划Agent] 处理完成")
    return {
        "response": result.get("response"),
        "intent": "create_delivery_plan",
        "generated_checklist": result.get("generated_checklist"),
        "generation_mode": result.get("generated_checklist", {}).get("generation_mode"),
        "llm_provider": result.get("generated_checklist", {}).get("llm_provider"),
        "suggested_actions": result.get("suggested_actions", []),
    }
