"""空间配置 Agent 工作流模块。"""
from app.agent.state import RenovatingAgentState
from app.agent.renovating_agent.nodes import (
    parse_requirements,
    recommend_product,
    generate_space_configuration,
    generate_smart_devices,
    generate_budget_range,
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
    parse_requirements,
    recommend_product,
    generate_space_configuration,
    generate_smart_devices,
    generate_budget_range,
    generate_response,
]


def create_renovating_agent_graph():
    """创建空间配置 Agent 工作流图；LangGraph 不可用时返回线性兜底。"""
    if StateGraph is None:
        return None
    graph = StateGraph(RenovatingAgentState)
    graph.add_node("parse_requirements", parse_requirements)
    graph.add_node("recommend_product", recommend_product)
    graph.add_node("generate_space_configuration", generate_space_configuration)
    graph.add_node("generate_smart_devices", generate_smart_devices)
    graph.add_node("generate_budget_range", generate_budget_range)
    graph.add_node("generate_response", generate_response)
    graph.set_entry_point("parse_requirements")
    graph.add_edge("parse_requirements", "recommend_product")
    graph.add_edge("recommend_product", "generate_space_configuration")
    graph.add_edge("generate_space_configuration", "generate_smart_devices")
    graph.add_edge("generate_smart_devices", "generate_budget_range")
    graph.add_edge("generate_budget_range", "generate_response")
    graph.add_edge("generate_response", END)
    return graph.compile()


_renovating_agent = None


def get_renovating_agent():
    global _renovating_agent
    if _renovating_agent is None:
        _renovating_agent = create_renovating_agent_graph()
    return _renovating_agent


async def _run_linear(initial_state: RenovatingAgentState) -> RenovatingAgentState:
    state = initial_state
    for node in NODES:
        state = await node(state)
    return state


async def run_renovating_agent(user_id: str, user_message: str, context: dict = None) -> dict:
    logger.info("[空间配置Agent] 开始处理 Demo 请求")
    initial_state: RenovatingAgentState = {
        "user_id": user_id,
        "user_message": user_message,
        "house_type": None,
        "house_area": None,
        "current_state": None,
        "style": None,
        "budget_range": None,
        "priorities": [],
        "budget_breakdown": {},
        "total_budget": None,
        "material_list": [],
        "phases": [],
        "total_days": 0,
        "acceptance_checklist": [],
        "response": None,
        "generated_plan": None,
        "suggested_actions": [],
        "error": None,
        "recommended_product": None,
        "recommended_area_sqm": None,
        "recommendation_reason": None,
        "target_guests": None,
        "operation_mode": None,
        "intelligence_level": None,
        "site_conditions": [],
        "space_modules": [],
        "configuration_items": [],
        "smart_devices": [],
        "decision_score": {},
    }
    if context:
        for key, value in context.items():
            initial_state[key] = value
    agent = get_renovating_agent()
    result = await agent.ainvoke(initial_state) if agent else await _run_linear(initial_state)
    logger.info("[空间配置Agent] 处理完成")
    return {
        "response": result.get("response"),
        "intent": "create_space_configuration",
        "generated_plan": result.get("generated_plan"),
        "generation_mode": result.get("generated_plan", {}).get("generation_mode"),
        "llm_provider": result.get("generated_plan", {}).get("llm_provider"),
        "suggested_actions": result.get("suggested_actions", []),
    }
