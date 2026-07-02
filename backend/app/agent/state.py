"""Agent 状态定义模块"""
from typing import TypedDict, List, Optional, Dict, Any


class MovingAgentState(TypedDict):
    """交付规划 Agent 状态。

    保留少量旧字段是为了兼容原 LangGraph 骨架；新的 PoC 字段位于
    confirmed_configuration、delivery_phases、site_risks 等字段。
    """
    user_id: str
    user_message: str
    source_address: Optional[str]
    target_address: Optional[str]
    source_rooms: List[str]
    target_rooms: List[str]
    moving_date: Optional[str]
    mover_count: Optional[int]
    vehicle_type: Optional[str]
    items: List[Dict[str, Any]]
    boxes: List[Dict[str, Any]]
    estimated_cost: Optional[float]
    cost_breakdown: Dict[str, float]
    unpacking_guide: List[Dict[str, Any]]
    response: Optional[str]
    generated_checklist: Optional[Dict[str, Any]]
    suggested_actions: List[str]
    error: Optional[str]
    confirmed_configuration: Dict[str, Any]
    delivery_phases: List[Dict[str, Any]]
    site_risks: List[Any]


class RenovatingAgentState(TypedDict):
    """空间配置 Agent 状态。

    保留少量旧字段是为了兼容原 LangGraph 骨架；新的 PoC 字段位于
    recommended_product、space_modules、configuration_items 等字段。
    """
    user_id: str
    user_message: str
    house_type: Optional[str]
    house_area: Optional[float]
    current_state: Optional[str]
    style: Optional[str]
    budget_range: Optional[str]
    priorities: List[str]
    budget_breakdown: Dict[str, float]
    total_budget: Optional[float]
    material_list: List[Dict[str, Any]]
    phases: List[Dict[str, Any]]
    total_days: int
    acceptance_checklist: List[Dict[str, Any]]
    response: Optional[str]
    generated_plan: Optional[Dict[str, Any]]
    suggested_actions: List[str]
    error: Optional[str]
    recommended_product: Optional[str]
    recommended_area_sqm: Optional[float]
    recommendation_reason: Optional[str]
    target_guests: Optional[str]
    operation_mode: Optional[str]
    intelligence_level: Optional[str]
    site_conditions: List[str]
    space_modules: List[str]
    configuration_items: List[str]
    smart_devices: List[str]
    decision_score: Dict[str, Any]
