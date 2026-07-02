"""交付规划 Agent 节点模块。

保留原 moving_agent 目录作为兼容入口，对外语义替换为"交付规划 Agent"。
当前 PoC 使用瑞泽·海度假民宿已建项目复盘规则生成交付看板。
"""
from app.agent.state import MovingAgentState
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
from app.llm.structured import generate_structured_json

logger = logging.getLogger(__name__)


def _load_knowledge() -> Dict[str, Any]:
    data_path = Path(__file__).resolve().parents[3] / "data" / "capsule_cabin_knowledge.json"
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _build_delivery_phases(knowledge: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
    ctx = context or {}
    product = ctx.get("recommended_product", "Capsule Cabin S")
    area = ctx.get("recommended_area_sqm", 38)
    intel = ctx.get("intelligence_level", "基础")
    is_m = area >= 56
    is_high_intel = intel == "标准"

    # 工厂/预制：56㎡需要更精细的模块尺寸核对
    factory_tasks = ["按确认方案进入工厂加工", "核对模块尺寸、材料、家具和智能设备预留", "跟踪材料到货与生产进度"]
    factory_risks = ["这是复盘中的高风险环节，材料到货、尺寸偏差和预留点位会影响现场安装"]
    if is_m:
        factory_tasks.extend(["核对拼装模块接口公差与预留点位对齐", "确认拼装模块分批出厂数量与顺序"])
        factory_risks.append("56㎡拼装模块需分批次出厂，接口公差和尺寸偏差会直接累积到现场拼接环节")

    # 运输：场地条件影响运输风险
    transport_tasks = ["核对运输尺寸", "确认道路条件与到场时间", "确认包装保护和临停空间"]
    transport_risks = ["道路运输、限高、转弯半径和现场临停条件可能影响到场"]
    if is_m:
        transport_tasks.append("核对多模块运输顺序与到场堆放协调")
        transport_risks.append("56㎡产品涉及多模块分批运输，需提前协调到场顺序与堆放空间")

    # 现场基础
    site_tasks = ["检查基础平整度", "确认排水、防水、防腐条件", "确认供电网络预留"]
    site_risks = ["基础不平、排水、防水、防腐和供电网络是现场复盘中的关键问题"]
    if is_m:
        site_tasks.append("确认双基础平整度与间距精度，预留拼装连接点位")
        site_risks.append("拼装产品需双基础精确对齐，基础间距偏差会影响拼接精度")

    # 吊装
    hoist_tasks = ["确认吊装空间", "按单体逐套推进吊装", "确认风力和现场安全条件"]
    hoist_risks = ["滨海场地需关注风、吊装空间和现场安全"]
    if is_m:
        hoist_tasks = ["确认吊装空间", "按模块顺序逐套推进吊装，拼装模块需精确对位", "确认风力和现场安全条件", "确认吊装设备承载能力与多模块协调作业方案"]
        hoist_risks.append("多模块吊装对吊臂作业半径、现场指挥协调要求更高")

    # 拼接安装：56㎡核心高风险环节
    splice_tasks = ["完成模块拼接", "检查连接、密封、防水节点", "核对隔音、隐私和空调体验"]
    splice_risks = ["这是复盘中的高风险环节，拼接精度、防水、隔音、隐私和空调容易被忽略"]
    if is_m:
        splice_tasks = [
            "完成模块拼接，逐接口核对公差与对位精度",
            "全面检查连接节点、密封条、防水涂层与排水坡度",
            "测试室内隔音效果、隐私隔断和空调系统分区温度",
            "验证两模块之间走线和水管接驳密封性",
            "现场修补与整改，形成拼接验收记录",
        ]
        splice_risks = ["56㎡拼装是最高风险环节：接口公差、密封、防水、隔音、空调分区与线缆接驳均需逐项验收"]

    # 调试验收
    debug_tasks = ["调试智能门锁、灯光、空调、窗帘、传感器、监控和网络", "核对配置清单", "整理验收问题清单"]
    debug_risks = ["这是复盘中的高风险环节，设备调试、网络和供电稳定性会影响无人化运营体验"]
    if is_high_intel:
        debug_tasks = [
            "逐台调试智能门锁、联网灯光系统、空调集中控制、电动窗帘",
            "测试传感器触发逻辑（入住/离房/温度/湿度）",
            "验证监控摄像头覆盖范围与网络回传稳定性",
            "联调自助入住流程：门锁→灯光→空调→窗帘自动场景",
            "核对配置清单，整理验收问题清单",
        ]
        debug_risks.append("标准智能化等级增加传感器联调、自助入住场景联调，需覆盖网络稳定性和传感器误触风险")

    return [
        {
            "phase": "设计确认",
            "tasks": ["生成业主方需求问卷", "确认产品型号、面积和入住人数边界", "确认空间模块、标配/选配和智能化等级"],
            "acceptance_criteria": ["形成已确认配置表", "关键需求进入面积与 BOM 控制清单"],
            "risks": ["需求端信息不完整会影响后续设计、BOM 和生产排期"],
            "human_confirmation_required": True,
        },
        {
            "phase": "工厂加工/预制",
            "tasks": factory_tasks,
            "acceptance_criteria": ["BOM 与配置表一致", "材料到货风险已标记", "关键预留点位完成出厂检查"],
            "risks": factory_risks,
            "human_confirmation_required": True,
        },
        {
            "phase": "运输",
            "tasks": transport_tasks,
            "acceptance_criteria": ["运输尺寸、道路条件和到场窗口经人工确认"],
            "risks": transport_risks,
            "human_confirmation_required": True,
        },
        {
            "phase": "现场基础",
            "tasks": site_tasks,
            "acceptance_criteria": ["基础、排水、防水、防腐、供电网络达到安装前置条件"],
            "risks": site_risks,
            "human_confirmation_required": True,
        },
        {
            "phase": "吊装",
            "tasks": hoist_tasks,
            "acceptance_criteria": ["吊装作业面、吊装顺序和现场安全条件经人工确认"],
            "risks": hoist_risks,
            "human_confirmation_required": True,
        },
        {
            "phase": "拼接安装",
            "tasks": splice_tasks,
            "acceptance_criteria": ["拼接节点、密封、防水和室内体验问题完成检查"],
            "risks": splice_risks,
            "human_confirmation_required": True,
        },
        {
            "phase": "调试验收",
            "tasks": debug_tasks,
            "acceptance_criteria": ["智能设备可用", "网络和供电稳定", "形成验收记录与开业前问题清单"],
            "risks": debug_risks,
            "human_confirmation_required": True,
        },
    ]


def _build_risk_assessment(configuration: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
    area = configuration.get("recommended_area_sqm", 38)
    product = configuration.get("recommended_product", "Capsule Cabin S")
    is_m = area >= 56
    site_risks = [
        {
            "category": "运输进场",
            "risk": "滨海场地道路较窄，大型运输车辆转弯半径不足，可能导致到场延误或二次转运。",
            "severity": "高",
            "mitigation": "提前勘察路线，确认限高、承载力、临停点与调头点，必要时采用小车分批转运。",
            "confirmation_owner": "施工方 + 运输方",
        },
        {
            "category": "吊装作业",
            "risk": "吊装空间有限时，吊车支腿展开、吊臂作业半径和风力条件会影响模块就位精度。",
            "severity": "高",
            "mitigation": "确认吊车吨位、臂长、支腿位置和作业面尺寸，形成吊装窗口与现场指挥方案。",
            "confirmation_owner": "施工方 + 业主",
        },
        {
            "category": "防腐防水",
            "risk": "滨海环境的盐雾、潮湿和暴雨积水会影响模块连接节点、防水层和金属紧固件寿命。",
            "severity": "中",
            "mitigation": "连接节点采用防腐紧固件，强化密封、防水涂层和排水坡度，并把节点检查写入验收项。",
            "confirmation_owner": "设计方 + 施工方",
        },
        {
            "category": "供电与网络",
            "risk": "供电容量、网络覆盖或弱电设备到货不稳定，会影响自助入住和智能设备调试。",
            "severity": "中",
            "mitigation": "提前确认供电容量、网络接入、备用电源和弱电设备到货时间，调试阶段做全链路测试。",
            "confirmation_owner": "运营方 + 电气设计",
        },
    ]
    if is_m:
        site_risks.append({
            "category": "拼装接口",
            "risk": "56㎡拼装产品涉及多模块接口，基础间距、模块公差、密封和线缆接驳会互相放大风险。",
            "severity": "高",
            "mitigation": "出厂前核对接口公差，到场后逐接口做密封、防水、隔音、线缆和管路接驳验收。",
            "confirmation_owner": "工厂 + 施工方 + 设计方",
        })

    return {
        "project_name": configuration.get("project_name", "瑞泽·海度假民宿交付风险评估"),
        "real_project_name": configuration.get("real_project_name", knowledge["real_project"]["name"]),
        "recommended_product": product,
        "recommended_area_sqm": area,
        "intent": "risk_assessment",
        "site_risks": site_risks,
        "pre_confirmation_items": [
            "确认道路转弯半径、限高、承载力，规划运输路线与临停方案",
            "确认吊车作业面尺寸、支腿位置、吊装半径与现场风力窗口",
            "确认基础平整度、基础间距、排水、防水、防腐方案",
            "确认供电容量、网络接入、弱电设备到货与备用电源方案",
            "确认消防、结构、安全和当地审批要求由专业人员复核",
        ],
        "high_risk_phases": knowledge["delivery"]["high_risk_phases"],
        "ai_opportunities": knowledge["ai_opportunities"],
        "data_source_note": knowledge["source_note"],
        "disclaimer": "风险评估为基于项目复盘的 AI PoC 输出，不构成正式工期、施工组织或工程承诺。",
        "generation_mode": "rule_fallback",
    }


def _is_risk_assessment_request(message: str) -> bool:
    text = message or ""
    risk_terms = ["风险", "评估", "前置确认", "确认项", "受限", "有限"]
    site_terms = ["吊装", "道路", "场地", "运输", "滨海", "防腐", "防水", "供电", "网络"]
    return any(term in text for term in risk_terms) and any(term in text for term in site_terms)


async def read_confirmed_configuration(state: MovingAgentState) -> MovingAgentState:
    """节点 1：读取已确认配置。"""
    logger.info("[交付规划Agent] 读取已确认配置")
    knowledge = _load_knowledge()
    confirmed = state.get("confirmed_configuration") or {}
    project = knowledge["real_project"]
    state["knowledge"] = knowledge
    state["confirmed_configuration"] = {
        "project_name": confirmed.get("project_name", "瑞泽·海度假民宿 38㎡单体扩建（规则型 PoC）"),
        "real_project_name": confirmed.get("real_project_name", project["name"]),
        "recommended_product": confirmed.get("recommended_product", "Capsule Cabin S"),
        "recommended_area_sqm": confirmed.get("recommended_area_sqm", 38),
        "operation_mode": confirmed.get("operation_mode", knowledge["operation"]["mode"] + "，自助入住 + 基础智能控制"),
        "intelligence_level": confirmed.get("intelligence_level", "基础"),
        "site_conditions": confirmed.get("site_conditions", knowledge["delivery"]["site_conditions"]),
    }
    return state


async def generate_delivery_phases(state: MovingAgentState) -> MovingAgentState:
    """节点 2：生成交付阶段。"""
    logger.info("[交付规划Agent] 生成交付阶段")
    knowledge = state.get("knowledge") or _load_knowledge()
    configuration = state.get("confirmed_configuration", {})
    context = {
        "recommended_product": configuration.get("recommended_product", "Capsule Cabin S"),
        "recommended_area_sqm": configuration.get("recommended_area_sqm", 38),
        "intelligence_level": configuration.get("intelligence_level", "基础"),
        "site_conditions": configuration.get("site_conditions", []),
    }
    state["delivery_phases"] = _build_delivery_phases(knowledge, context)
    return state


async def generate_phase_tasks(state: MovingAgentState) -> MovingAgentState:
    """节点 3：生成每阶段任务与验收点。"""
    logger.info("[交付规划Agent] 生成任务与验收点")
    return state


async def generate_site_risks(state: MovingAgentState) -> MovingAgentState:
    """节点 4：生成现场风险提示。"""
    logger.info("[交付规划Agent] 生成现场风险提示")
    knowledge = state.get("knowledge") or _load_knowledge()
    state["site_risks"] = [
        "滨海环境风险：" + "、".join(knowledge["risks"]["coastal"]) + "。",
        "现场交付条件：" + "、".join(knowledge["delivery"]["site_conditions"]) + "需提前确认。",
        "现场施工最大风险之一是材料到货，需联动 BOM 与生产进度。",
        "室内体验易忽略隔音、隐私和空调，需要进入验收清单。",
        "消防、结构、安全和审批要求不由 PoC 自动确认。"
    ]
    return state


async def generate_response(state: MovingAgentState) -> MovingAgentState:
    """节点 5：输出交付看板数据。"""
    logger.info("[交付规划Agent] 输出交付看板数据")
    knowledge = state.get("knowledge") or _load_knowledge()
    configuration = state.get("confirmed_configuration", {})
    user_msg = state.get("user_message", "")
    phases = state.get("delivery_phases", [])

    # 检测用户意图：风险评估 vs 生成看板
    is_risk_request = _is_risk_assessment_request(user_msg)

    dashboard = {
        "project_name": configuration.get("project_name"),
        "real_project_name": configuration.get("real_project_name"),
        "recommended_product": configuration.get("recommended_product"),
        "recommended_area_sqm": configuration.get("recommended_area_sqm"),
        "delivery_phases": phases,
        "site_risks": state.get("site_risks", []),
        "high_risk_phases": knowledge["delivery"]["high_risk_phases"],
        "ai_opportunities": knowledge["ai_opportunities"],
        "data_source_note": knowledge["source_note"],
        "disclaimer": "交付阶段、任务与风险均为基于项目复盘的 AI PoC 输出，不构成正式工期、施工组织或工程承诺。",
        "generation_mode": "rule_fallback",
        "intent": "risk_assessment" if is_risk_request else "delivery_board",
    }

    if is_risk_request:
        dashboard = _build_risk_assessment(configuration, knowledge)
        # 风险评估模式：聚焦场地风险和前置确认项
        system_prompt = """你是"瑞泽·海度假民宿"的交付规划 Agent，当前任务是针对场地条件进行风险评估。
必须遵守：
1. 只基于输入的项目复盘规则和场地条件分析，不编造工期、报价或审批结论。
2. 输出结构必须包含以下字段：
   - intent: "risk_assessment"
   - site_risks: 数组，每个风险含 category、risk、severity(高/中/低)、mitigation、confirmation_owner
   - pre_confirmation_items: 数组，列出开工前必须人工确认的事项
   - response: 简洁中文 Markdown，汇总关键风险和建议
3. 输出必须是一个 JSON object，不要 Markdown 代码块。"""
        user_prompt = f"""用户请求：
{user_msg}

已确认配置：
{json.dumps(configuration, ensure_ascii=False)}

项目复盘中的场地与风险知识：
{json.dumps({
    "delivery": knowledge["delivery"],
    "risks": knowledge["risks"],
    "site_conditions": knowledge["delivery"]["site_conditions"],
    "high_risk_phases": knowledge["delivery"]["high_risk_phases"],
}, ensure_ascii=False)}

规则引擎草案中的阶段任务：
{json.dumps(phases, ensure_ascii=False)}

请基于用户的具体场景（如道路窄、吊装空间有限），聚焦评估该场景下的交付风险，输出风险清单与前置确认项。直接返回 JSON。"""
    else:
        # 标准看板模式
        system_prompt = """你是"瑞泽·海度假民宿"的交付规划 Agent，负责把已确认配置转成装配式交付看板。
必须遵守：
1. 基于输入的配置和项目复盘规则生成，不编造正式工期、报价、审批或施工承诺。
2. 必须保留 7 个核心阶段：设计确认、工厂加工/预制、运输、现场基础、吊装、拼接安装、调试验收。
3. 每个阶段都要有 tasks、acceptance_criteria、risks、human_confirmation_required。
4. 输出必须是一个 JSON object，不要 Markdown 代码块，不要额外解释。"""
        user_prompt = f"""用户请求：
{user_msg}

已确认配置：
{json.dumps(configuration, ensure_ascii=False)}

项目复盘知识：
{json.dumps({
    "real_project": knowledge["real_project"],
            "delivery": knowledge["delivery"],
            "risks": knowledge["risks"],
            "operation": knowledge["operation"],
            "source_note": knowledge["source_note"],
        }, ensure_ascii=False)}

规则引擎草案：
{json.dumps(dashboard, ensure_ascii=False)}

请基于规则草案，只补充 response 字段：简洁中文 Markdown，说明已调用 LLM 在规则约束下生成，指出规则未覆盖的风险或建议。其余字段沿用规则草案。直接返回 JSON。"""

    result = await generate_structured_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        fallback=dashboard,
    )
    if is_risk_request:
        result["intent"] = "risk_assessment"
        valid_risks = [
            risk for risk in result.get("site_risks", [])
            if isinstance(risk, dict) and risk.get("risk")
        ]
        if not valid_risks:
            result["site_risks"] = dashboard["site_risks"]
        if not result.get("pre_confirmation_items"):
            result["pre_confirmation_items"] = dashboard.get("pre_confirmation_items", [])
    result["data_source_note"] = knowledge["source_note"]
    result["disclaimer"] = result.get("disclaimer") or "交付阶段、任务与风险均为基于项目复盘的 AI PoC 输出，不构成正式工期、施工组织或工程承诺。"
    phases = result.get("delivery_phases") or phases
    if result.get("intent") == "risk_assessment":
        risk_lines = [
            f"{risk.get('category')}：{risk.get('risk')}（{risk.get('severity')}）"
            for risk in result.get("site_risks", [])
            if isinstance(risk, dict)
        ]
        response = f"""**交付规划 Agent 已基于案例规则生成风险评估**

真实项目：{result['real_project_name']}

产品：{result['recommended_product']}（约 {result['recommended_area_sqm']}㎡）

重点风险：{'; '.join(risk_lines)}

前置确认：{'; '.join(result.get('pre_confirmation_items', []))}
"""
    else:
        response = f"""**交付规划 Agent 已基于案例规则生成看板**

真实项目：{result['real_project_name']}

产品：{result['recommended_product']}（约 {result['recommended_area_sqm']}㎡）

交付阶段：{len(phases)} 个阶段

高风险环节：{', '.join(result['high_risk_phases'])}

阶段列表：{', '.join(phase['phase'] for phase in phases)}

重点风险：{'; '.join(result['site_risks'])}
"""
    if result.get("response"):
        response = result["response"]
    elif result.get("generation_mode") == "llm_with_rule_guardrails":
        response = response.replace("已基于案例规则生成看板", "已调用 LLM 在案例规则约束下生成看板")

    state["response"] = response
    state["generated_checklist"] = result
    state["suggested_actions"] = ["查看交付看板", "查看数据来源", "返回调整配置"]
    return state
