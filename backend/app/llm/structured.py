"""LLM 结构化输出工具。"""
from typing import Any, Dict, Optional
import json
import logging

from app.llm.client import get_llm_client

logger = logging.getLogger(__name__)


def build_llm_guardrail_insights(fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Build a display-friendly insight block when the model text is not strict JSON."""
    product = fallback.get("recommended_product") or fallback.get("product") or "当前推荐产品"
    area = fallback.get("recommended_area_sqm") or fallback.get("area_sqm") or fallback.get("area") or ""
    area_label = f"{area}㎡" if area else "当前面积口径"

    if fallback.get("delivery_phases"):
        return {
            "summary": f"LLM 已调用并在规则护栏下复核交付拆解，当前以 {product} / {area_label} 为输入，把设计确认、工厂预制、运输、现场基础、吊装、拼接安装和调试验收拆成可执行任务。",
            "owner_questions": [
                "最终吊装窗口、道路进场条件和临停位置是否已确认？",
                "供电、网络、排水、防水和防腐责任边界由谁验收？",
                "哪些交付节点需要业主、施工方和运营方共同签字？",
            ],
            "tradeoffs": [
                "工厂预制越完整，现场工期越短，但前置确认和 BOM 冻结要求更高。",
                "无人化运营配置越高，后期维护成本和网络稳定性要求也越高。",
            ],
            "risk_watchpoints": [
                "滨海风、潮湿、盐雾对吊装安全、密封、防腐和机电稳定性影响较大。",
                "基础不平、预留点位偏差和网络不稳定会直接影响最终验收。",
            ],
        }

    return {
        "summary": f"LLM 已调用并在规则护栏下复核业主需求，当前推荐 {product} / {area_label}；结论仍受既有项目复盘、产品资料和人工确认边界约束。",
        "owner_questions": [
            "实际峰值入住人数、亲子或小团体比例是否明确？",
            "是否需要做饭、活动区、长期收纳或灵活变换空间？",
            "自助入住要覆盖哪些设备：门锁、灯光、空调、窗帘、监控、传感器还是全套？",
        ],
        "tradeoffs": [
            "56㎡拼装更适合多人和活动区，但运输、吊装、基础和预算压力更高。",
            "38㎡单体更利于快速复制和控成本，但多人入住体验与功能拓展空间有限。",
        ],
        "risk_watchpoints": [
            "滨海场地需要提前确认防腐、防水、潮湿、风、排水和供电网络。",
            "配置清单只能作为 PoC 方案输入，正式报价、消防、结构和审批仍需人工确认。",
        ],
    }


def extract_json_object(text: str) -> Dict[str, Any]:
    """从模型回复中提取第一个 JSON object。"""
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("LLM 回复中没有 JSON object")
    return json.loads(raw[start:end + 1])


async def generate_structured_json(
    *,
    system_prompt: str,
    user_prompt: str,
    fallback: Dict[str, Any],
) -> Dict[str, Any]:
    """优先调用 LLM 生成 JSON，失败时返回规则兜底。"""
    try:
        client = get_llm_client()
        if not client.is_configured():
            return {
                **fallback,
                "generation_mode": "rule_fallback",
                "llm_error": "LLM API Key 未配置",
            }

        text = await client.acomplete(user_prompt, system_prompt=system_prompt)
        try:
            generated = extract_json_object(text)
        except Exception as parse_exc:
            logger.warning("LLM 回复不是严格 JSON，使用规则结构承载 LLM 文本: %s", parse_exc)
            insights = build_llm_guardrail_insights(fallback)
            generated = {
                "response": f"**已调用 LLM 在规则约束下生成输出**\n\n{insights['summary']}",
                "llm_insights": insights,
            }
        if generated.get("response") and "已调用 LLM" not in generated["response"]:
            generated["response"] = "**已调用 LLM 在规则约束下生成输出**\n\n" + generated["response"]
        return {
            **fallback,
            **generated,
            "generation_mode": "llm_with_rule_guardrails",
            "llm_provider": client.provider,
            "llm_error": None,
        }
    except Exception as exc:
        logger.warning("结构化 LLM 生成失败，使用规则兜底: %s", exc)
        return {
            **fallback,
            "generation_mode": "rule_fallback",
            "llm_error": str(exc),
        }
