"""空间配置 Agent 节点模块。

保留原 renovating_agent 目录作为兼容入口，对外语义替换为
“瑞泽·海度假民宿空间配置 Agent”。当前 PoC 使用真实项目复盘规则兜底，
用于保证无 LLM 时也能稳定演示。
"""
from app.agent.state import RenovatingAgentState
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import json
import logging
import re
from app.llm.structured import generate_structured_json

logger = logging.getLogger(__name__)


DISCLAIMER = "示例配置预算区间，仅用于规则型 PoC 演示，不构成正式报价、设计或施工承诺。"


def _load_knowledge() -> Dict[str, Any]:
    data_path = Path(__file__).resolve().parents[3] / "data" / "capsule_cabin_knowledge.json"
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _extract_guest_count(message: str) -> Optional[int]:
    text = message or ""
    digit_match = re.search(r"(\d+)\s*(个人|人|位|名|口)", text)
    if digit_match:
        return int(digit_match.group(1))
    chinese_digits = {
        "一": 1,
        "二": 2,
        "两": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
        "十": 10,
    }
    chinese_match = re.search(r"([一二两三四五六七八九十])\s*(个人|人|位|名|口)", text)
    return chinese_digits.get(chinese_match.group(1)) if chinese_match else None


def _infer_product(message: str, knowledge: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    text = message or ""
    products = {item["model"]: item for item in knowledge["products"]}
    m_product = products["Capsule Cabin M"]
    s_product = products["Capsule Cabin S"]
    guest_count = _extract_guest_count(text)
    if guest_count and guest_count > 4:
        return (
            m_product,
            f"输入中包含 {guest_count} 人入住，已超过 38㎡单体最多 4 人的舒适接待边界，优先匹配 56㎡拼装产品；仍需人工确认是否采用单套 56㎡、双套组合或加床策略。",
        )
    m_keywords = ["亲子", "家庭", "小团体", "多人", "56", "做饭", "活动区", "宽松", "灵活"]
    if any(keyword in text for keyword in m_keywords):
        return (
            m_product,
            "输入中包含多人入住、亲子/小团体、做饭、活动区或空间宽松需求，匹配瑞泽·海项目复盘中 56㎡拼装产品的适用场景。",
        )
    return (
        s_product,
        "输入以单体扩建、面积控制或标准房型为主，匹配瑞泽·海项目中 38㎡单体产品的紧凑型配置经验；该产品最多可支持 4 人入住。",
    )


def _is_intelligence_upgrade(message: str) -> bool:
    text = message or ""
    return any(keyword in text for keyword in ["智能化等级", "升级", "标准智能", "更高智能", "新增设备", "调试风险"])


def _product_by_model(model: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
    products = {item["model"]: item for item in knowledge["products"]}
    return products.get(model) or products["Capsule Cabin S"]


def _build_upgrade_delta(plan: Dict[str, Any]) -> Dict[str, Any]:
    area = plan.get("recommended_area_sqm", 38)
    product = plan.get("recommended_product", "Capsule Cabin S")
    is_m = area >= 56
    return {
        "type": "intelligence_level_upgrade",
        "from_level": "基础",
        "to_level": "标准",
        "kept_product": product,
        "kept_area_sqm": area,
        "summary": f"本次不是重新选型，而是在已确认的 {product} / {area}㎡ 方案上，把智能化等级从基础升级到标准。",
        "added_devices": [
            "全屋智能客控系统",
            "大屏幕投影设备",
            "入住/离房场景联动",
            "温湿度或人体存在传感器",
            "网络稳定性与远程运维监测",
        ],
        "commissioning_risks": [
            "门锁、灯光、空调、窗帘和传感器联动逻辑需要现场逐项测试。",
            "标准智能化更依赖网络稳定性，弱电到货、布线和信号覆盖要前置确认。",
            "自助入住链路故障会直接影响运营体验，需要保留人工应急开门和设备重置方案。",
        ] + ([
            "56㎡拼装方案还需检查跨模块走线、网络覆盖和传感器覆盖盲区。"
        ] if is_m else []),
        "acceptance_points": [
            "完成门锁到灯光、空调、窗帘的入住场景联调。",
            "验证离房节能、异常告警和远程重置能力。",
            "检查监控覆盖、隐私边界和网络回传稳定性。",
            "形成智能设备点位、账号权限和运维交接清单。",
        ],
    }


def _score_decision(message: str, knowledge: Dict[str, Any], recommended_product: str) -> Dict[str, Any]:
    text = message or ""
    guest_count = _extract_guest_count(text)
    score_m = 0
    score_s = 0
    signals: list = []

    # 入住人数
    if guest_count and guest_count > 4:
        score_m += 3
        signals.append({"dimension": "入住人数", "value": f"{guest_count} 人", "reason": "超过 4 人舒适边界", "confidence": 0.9})
    elif guest_count and guest_count <= 2:
        score_s += 2
        signals.append({"dimension": "入住人数", "value": f"{guest_count} 人", "reason": "单体即可满足", "confidence": 0.85})
    else:
        signals.append({"dimension": "入住人数", "value": "未明确或 3~4 人", "reason": "按默认单体推荐", "confidence": 0.6})

    # 做饭需求
    cook_keywords = ["做饭", "简餐", "烹饪", "厨房", "餐区"]
    if any(k in text for k in cook_keywords):
        score_m += 2
        signals.append({"dimension": "做饭/餐区需求", "value": "需要", "reason": "简餐/活动区需更大空间", "confidence": 0.85})
    else:
        signals.append({"dimension": "做饭/餐区需求", "value": "未提及", "reason": "默认不含烹饪区", "confidence": 0.7})

    # 活动区需求
    activity_keywords = ["活动区", "活动空间", "客厅", "宽敞", "宽松", "灵活"]
    if any(k in text for k in activity_keywords):
        score_m += 2
        signals.append({"dimension": "活动区需求", "value": "需要", "reason": "需更大公共活动空间", "confidence": 0.8})
    else:
        signals.append({"dimension": "活动区需求", "value": "未提及", "reason": "按紧凑型标准配置", "confidence": 0.7})

    # 运营方式
    operation = knowledge.get("operation", {}).get("mode", "")
    if any(k in text for k in ["自助", "无人"]):
        signals.append({"dimension": "运营方式", "value": "自助入住", "reason": "用户明确提及自助/无人", "confidence": 0.9})
    else:
        signals.append({"dimension": "运营方式", "value": "自助入住（默认）", "reason": "按案例默认自助入住 + 基础智能", "confidence": 0.75})

    # 智能化等级
    if any(k in text for k in ["更高", "标准", "智能升级"]):
        score_m += 1
        signals.append({"dimension": "智能化等级", "value": "标准智能化", "reason": "用户明确要求升级智能", "confidence": 0.9})
    elif any(k in text for k in ["智能", "无人", "自助"]):
        signals.append({"dimension": "智能化等级", "value": "基础智能控制", "reason": "默认基础智能", "confidence": 0.7})
    else:
        signals.append({"dimension": "智能化等级", "value": "基础", "reason": "未提及，按最简配置", "confidence": 0.65})

    # 场地约束
    site_conditions = knowledge.get("delivery", {}).get("site_conditions", [])
    if any(k in text for k in ["吊装", "场地", "防腐", "滨海", "狭窄"]):
        signals.append({"dimension": "场地约束", "value": "用户已感知场地风险", "reason": "提及吊装/场地/防腐等关键词", "confidence": 0.85})
    else:
        signals.append({"dimension": "场地约束", "value": "按复盘默认（滨海）", "reason": "瑞泽·海复盘场景为滨海场地", "confidence": 0.7})

    # 预算档位
    if any(k in text for k in ["高档", "高端", "豪华", "精品"]):
        score_m += 1
        signals.append({"dimension": "预算档位", "value": "中高档", "reason": "关键词指向高端需求", "confidence": 0.75})
    elif any(k in text for k in ["预算", "控制", "经济", "性价比"]):
        score_s += 1
        signals.append({"dimension": "预算档位", "value": "预算敏感", "reason": "用户明确要求控制预算", "confidence": 0.75})
    else:
        signals.append({"dimension": "预算档位", "value": "中档（默认）", "reason": "未明确，默认中档配置", "confidence": 0.6})

    # 决策结论
    winner = "56㎡" if score_m > score_s else "38㎡"
    confidence = round(max(score_m, score_s) / (score_m + score_s + 0.01), 2)
    return {
        "product_vote": winner,
        "score_s": score_s,
        "score_m": score_m,
        "confidence": confidence,
        "signals": signals,
        "recommended_product": recommended_product,
    }


async def parse_requirements(state: RenovatingAgentState) -> RenovatingAgentState:
    """节点 1：解析民宿需求。"""
    logger.info("[空间配置Agent] 解析民宿需求")
    knowledge = _load_knowledge()
    message = state.get("user_message", "")
    previous_configuration = state.get("configuration") or state.get("previous_configuration") or {}
    is_upgrade = _is_intelligence_upgrade(message) and bool(previous_configuration)
    if is_upgrade:
        product = _product_by_model(previous_configuration.get("recommended_product", "Capsule Cabin S"), knowledge)
        reason = (
            f"本次识别为智能化升级请求，保留上一轮 {product['model']} / "
            f"{previous_configuration.get('recommended_area_sqm', product['area_sqm'])}㎡ 选型，只调整智能化等级与验收要求。"
        )
    else:
        product, reason = _infer_product(message, knowledge)
    operation = knowledge["operation"]
    project = knowledge["real_project"]
    state["knowledge"] = knowledge
    state["real_project_name"] = project["name"]
    state["recommended_product"] = product["model"]
    state["recommended_area_sqm"] = previous_configuration.get("recommended_area_sqm", product["area_sqm"]) if is_upgrade else product["area_sqm"]
    state["recommendation_reason"] = reason
    state["target_guests"] = previous_configuration.get("target_guests", product["positioning"]) if is_upgrade else product["positioning"]
    state["style"] = previous_configuration.get("style", "柔和粉白色系，海滨轻度假") if is_upgrade else "柔和粉白色系，海滨轻度假"
    state["operation_mode"] = operation["mode"] + "，自助入住 + 标准智能控制" if is_upgrade else operation["mode"] + "，自助入住 + 基础智能控制"
    state["intelligence_level"] = "标准" if is_upgrade or "标准" in message or "更高" in message or "升级" in message else "基础"
    state["site_conditions"] = previous_configuration.get("site_conditions", knowledge["delivery"]["site_conditions"]) if is_upgrade else knowledge["delivery"]["site_conditions"]
    state["decision_score"] = _score_decision(message, knowledge, product["model"])
    state["upgrade_mode"] = is_upgrade
    state["previous_configuration"] = previous_configuration
    return state


async def recommend_product(state: RenovatingAgentState) -> RenovatingAgentState:
    """节点 2：推荐产品型号。"""
    logger.info("[空间配置Agent] 推荐产品型号")
    if not state.get("recommended_product"):
        knowledge = state.get("knowledge") or _load_knowledge()
        product, reason = _infer_product(state.get("user_message", ""), knowledge)
        state["recommended_product"] = product["model"]
        state["recommended_area_sqm"] = product["area_sqm"]
        state["recommendation_reason"] = reason
    return state


async def generate_space_configuration(state: RenovatingAgentState) -> RenovatingAgentState:
    """节点 3：生成空间模块与室内配置。"""
    logger.info("[空间配置Agent] 生成空间模块与室内配置")
    knowledge = state.get("knowledge") or _load_knowledge()
    product = next(item for item in knowledge["products"] if item["model"] == state.get("recommended_product"))
    standard = knowledge["standard_configuration"]
    optional = knowledge["optional_configuration"]
    previous = state.get("previous_configuration") or {}
    config = list(previous.get("configuration_items", [])) if state.get("upgrade_mode") else []
    if not config:
        config.extend(standard["core_furniture"])
        config.extend(["干湿分离卫浴", "24小时冷水/定时热水", "电热水壶、茶包/咖啡、瓶装水"])
        config.extend(["空调/供暖设备", "220V电源插座", "烟雾报警器等消防设施", "稳定 Wi-Fi", "电视"])
    if state.get("intelligence_level") == "标准":
        for item in optional["smart_and_tech"]:
            if item not in config:
                config.append(item)
    state["space_modules"] = previous.get("space_modules", product["space_modules"]) if state.get("upgrade_mode") else product["space_modules"]
    state["configuration_items"] = config
    state["optional_items"] = optional["smart_and_tech"]
    return state


async def generate_smart_devices(state: RenovatingAgentState) -> RenovatingAgentState:
    """节点 4：生成基础智能设备建议。"""
    logger.info("[空间配置Agent] 生成智能设备建议")
    knowledge = state.get("knowledge") or _load_knowledge()
    devices = list(knowledge["operation"]["smart_devices"])
    if state.get("intelligence_level") == "标准":
        for item in ["全屋智能客控系统", "投影设备", "远程运维监测"]:
            if item not in devices:
                devices.append(item)
    state["smart_devices"] = devices
    return state


async def generate_budget_range(state: RenovatingAgentState) -> RenovatingAgentState:
    """节点 5：生成示例预算区间说明。"""
    logger.info("[空间配置Agent] 生成示例预算区间")
    state["budget_range"] = {
        "level": "中档" if state.get("intelligence_level") == "基础" else "中高档",
        "categories": ["模块化建筑", "室内集成", "家具软装", "智能设备", "运输吊装", "调试验收"],
        "note": DISCLAIMER,
    }
    return state


async def generate_response(state: RenovatingAgentState) -> RenovatingAgentState:
    """节点 6：输出结构化方案。"""
    logger.info("[空间配置Agent] 输出结构化方案")
    knowledge = state.get("knowledge") or _load_knowledge()
    project = knowledge["real_project"]
    product = next(item for item in knowledge["products"] if item["model"] == state.get("recommended_product"))
    recommendation_basis = [
        product["positioning"],
        "运营侧关注入住效率、维护成本、拍照传播和舒适度。",
        "自助入住场景需要智能门锁、灯光、空调、窗帘、传感器、监控与稳定网络。",
        "滨海场地需要提前关注防腐、防水、潮湿、风、排水、供电网络和吊装条件。"
    ]
    ai_opportunities = knowledge["ai_opportunities"]
    area = state.get("recommended_area_sqm")
    plan = {
        "project_name": "瑞泽·海度假民宿 56㎡拼装配置" if area and area >= 56 else "瑞泽·海度假民宿 38㎡单体扩建",
        "real_project_name": project["name"],
        "project_location_display": project["location_display"],
        "product_system": project["product_system"],
        "recommended_product": state.get("recommended_product"),
        "recommended_area_sqm": state.get("recommended_area_sqm"),
        "recommendation_reason": state.get("recommendation_reason"),
        "recommendation_basis": recommendation_basis,
        "target_guests": state.get("target_guests"),
        "style": state.get("style"),
        "operation_mode": state.get("operation_mode"),
        "intelligence_level": state.get("intelligence_level"),
        "site_conditions": state.get("site_conditions", []),
        "space_modules": state.get("space_modules", []),
        "configuration_items": state.get("configuration_items", []),
        "optional_items": state.get("optional_items", []),
        "smart_devices": state.get("smart_devices", []),
        "budget_range": state.get("budget_range", {}),
        "data_source_note": knowledge["source_note"],
        "ai_opportunities": ai_opportunities,
        "human_confirmation_required": [
            "业主方需求问卷与入住人数边界",
            "面积、BOM 表与配置层级",
            "材料到货与生产端进度",
            "现场基础、吊装、道路运输、排水、防水、防腐、供电网络",
            "消防、结构、安全和当地审批要求"
        ],
        "disclaimer": "基于瑞泽·海度假民宿已建项目经验复盘的 AI PoC，不替代专业设计与工程管理。",
        "generation_mode": "rule_fallback",
        "decision_score": state.get("decision_score", {}),
    }
    if state.get("upgrade_mode"):
        plan["project_name"] = plan["project_name"] + "｜标准智能化升级"
        plan["recommendation_reason"] = state.get("recommendation_reason")
        plan["upgrade_delta"] = _build_upgrade_delta(plan)
    system_prompt = """你是“瑞泽·海度假民宿”的空间配置 Agent，负责把业主需求转成装配式胶囊客房配置方案。
必须遵守：
1. 只能基于输入的真实项目复盘、产品资料和规则草案生成，不编造价格、工期、审批结论。
2. 保留推荐产品、面积、真实项目名、产品体系等关键事实，不要随意改型号。
3. 除了复述方案，还要体现 LLM 的价值：补充业主侧取舍、待确认问题、风险关注点。
4. 输出必须是一个 JSON object，不要 Markdown 代码块，不要额外解释。"""
    user_prompt = f"""用户需求：
{state.get("user_message", "")}

真实项目与产品知识：
{json.dumps({
    "real_project": project,
    "products": knowledge["products"],
    "operation": knowledge["operation"],
    "risks": knowledge["risks"],
    "delivery_site_conditions": knowledge["delivery"]["site_conditions"],
    "source_note": knowledge["source_note"],
}, ensure_ascii=False)}

规则引擎草案：
{json.dumps(plan, ensure_ascii=False)}

请基于规则草案，只补充以下两个字段，其余字段沿用规则草案：
1. llm_insights: 对象，含 summary(2句)、owner_questions(3条)、tradeoffs(3条)、risk_watchpoints(3条)
2. response: 简洁中文 Markdown，说明”已调用 LLM 在规则约束下生成”，突出规则模板未覆盖的判断。
直接返回 JSON，不要 Markdown 代码块。"""
    plan = await generate_structured_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        fallback=plan,
    )
    if plan.get("generation_mode") == "llm_with_rule_guardrails" and not plan.get("llm_insights"):
        plan["llm_insights"] = {
            "summary": "LLM 已在项目复盘规则约束下复核该方案，并把推荐结果转成更适合业主沟通的配置判断。",
            "owner_questions": [
                "多人入住的主要客群是亲子、朋友结伴还是小团体活动？",
                "是否需要保留简餐/烹饪区，还是优先扩大休息与收纳空间？",
                "现场吊装窗口、临停空间、供电网络是否已经确认？",
            ],
            "tradeoffs": [
                "56㎡拼装更适合多人入住，但运输、吊装和拼接验收复杂度高于 38㎡单体。",
                "提高智能化等级能降低自助入住运营压力，但会增加调试和网络稳定性要求。",
                "活动区与收纳区需要在空间感和维护效率之间做取舍。",
            ],
            "risk_watchpoints": [
                "滨海环境下的防腐、防水、潮湿和风荷载需要前置确认。",
                "模块拼接处的密封、防水、隔音和空调体验需要进入验收清单。",
                "BOM、生产排期、运输到场和吊装窗口必须同步管理。",
            ],
        }
    plan["data_source_note"] = knowledge["source_note"]
    plan["disclaimer"] = "基于瑞泽·海度假民宿已建项目经验复盘的 AI PoC，不替代专业设计与工程管理。"
    response = f"""**空间配置 Agent 已基于案例规则生成方案**

真实项目：{plan['real_project_name']}（{plan['project_location_display']}）

产品体系：{plan['product_system']}

推荐产品：{plan['recommended_product']}（约 {plan['recommended_area_sqm']}㎡）

推荐理由：{plan['recommendation_reason']}

空间模块：{', '.join(plan['space_modules'])}

配置清单：{', '.join(plan['configuration_items'][:10])} 等

智能设备：{', '.join(plan['smart_devices'])}

推荐依据：{'; '.join(plan['recommendation_basis'])}

预算说明：{plan['budget_range'].get('level')}配置层级。{plan['budget_range'].get('note')}
"""
    if plan.get("response"):
        response = plan["response"]
    elif plan.get("generation_mode") == "llm_with_rule_guardrails":
        response = response.replace("已基于案例规则生成方案", "已调用 LLM 在案例规则约束下生成方案")

    state["response"] = response
    state["generated_plan"] = plan
    state["suggested_actions"] = ["生成交付阶段与验收任务", "查看推荐依据", "调整智能化等级"]
    return state
