"""Agent 对话 API 模块"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pathlib import Path
from typing import Tuple
import json
from app.database import get_db
from app.models.project import Project, Conversation, Checklist, ChecklistItem, Budget, Phase
from app.agent.moving_agent.graph import run_moving_agent
from app.agent.renovating_agent.graph import run_renovating_agent
import logging

router = APIRouter(prefix="/api/v1/agent")
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


def _load_demo_case() -> dict:
    data_path = Path(__file__).resolve().parents[2] / "data" / "demo_capsule_cabin.json"
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_case_knowledge() -> dict:
    data_path = Path(__file__).resolve().parents[2] / "data" / "capsule_cabin_knowledge.json"
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _is_delivery_request(message: str) -> bool:
    text = message or ""
    is_upgrade = "升级" in text or "智能化等级" in text
    if is_upgrade:
        return False
    strong_keywords = ["交付看板", "交付阶段", "交付风险", "生成交付", "装配式交付"]
    return any(keyword in text for keyword in strong_keywords)


def get_current_user_id(token: str) -> str:
    from jose import jwt
    from app.config import settings
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的认证凭证")
        return user_id
    except:
        raise HTTPException(status_code=401, detail="未授权")


def detect_project_type(message: str) -> Tuple[str, bool]:
    """检测 PoC 业务意图，返回 (project_type, is_detected)。"""
    text = message or ""
    if _is_delivery_request(text) or any(kw in text for kw in ["交付风险", "吊装", "运输", "调试", "验收", "看板", "前置确认"]):
        return "delivery_planning", True
    if any(kw in text for kw in ["配置", "户型", "38", "56", "智能", "亲子", "多人", "单体", "拼装", "卡素", "民宿", "扩建"]):
        return "space_configuration", True
    return "space_configuration", False


@router.get("/demo-case")
async def get_demo_case():
    """规则型 PoC 固定案例。"""
    return _load_demo_case()


@router.post("/demo-chat")
async def chat_with_demo_agent(request: dict):
    """规则型 PoC 对话入口。

    不依赖登录和生产数据库。空间配置与交付规划优先使用瑞泽·海度假民宿
    已建项目复盘规则兜底，用于作品集演示闭环。
    """
    message = request.get("message", "")
    context = request.get("context", {})
    if _is_delivery_request(message) or request.get("agent") == "delivery":
        result = await run_moving_agent(
            user_id=DEMO_USER_ID,
            user_message=message,
            context={"confirmed_configuration": context.get("configuration") or context},
        )
        return {
            "message": result.get("response", ""),
            "intent": result.get("intent"),
            "agent": "delivery_planning",
            "project_type": "capsule_cabin_demo",
            "generated_delivery": result.get("generated_checklist"),
            "generated_plan": None,
            "generation_mode": result.get("generation_mode"),
            "llm_provider": result.get("llm_provider"),
            "suggested_actions": result.get("suggested_actions", []),
        }

    result = await run_renovating_agent(user_id=DEMO_USER_ID, user_message=message, context=context)
    return {
        "message": result.get("response", ""),
        "intent": result.get("intent"),
        "agent": "space_configuration",
        "project_type": "capsule_cabin_demo",
        "generated_plan": result.get("generated_plan"),
        "generated_delivery": None,
        "generation_mode": result.get("generation_mode"),
        "llm_provider": result.get("llm_provider"),
        "suggested_actions": result.get("suggested_actions", []),
    }


@router.get("/demo-project")
async def get_demo_project():
    """规则型 PoC 项目详情数据，供截图页直接展示。"""
    demo = _load_demo_case()
    knowledge = _load_case_knowledge()
    configuration = await run_renovating_agent(
        user_id=DEMO_USER_ID,
        user_message="基于瑞泽·海度假民宿复盘，为滨海度假区新增一套 38㎡卡素单体产品，自助入住，配置基础智能控制。",
        context={},
    )
    delivery = await run_moving_agent(
        user_id=DEMO_USER_ID,
        user_message="根据已确认的 38㎡方案生成交付阶段与验收任务。",
        context={"confirmed_configuration": configuration.get("generated_plan", {})},
    )
    return {
        "id": "demo-capsule-cabin",
        "title": demo["project_name"],
        "project_type": "capsule_cabin_demo",
        "status": "demo",
        "requirements": {
            "product_model": demo["product_series"],
            "target_guests": demo["target_guests"],
            "operation_mode": demo["operation_mode"],
            "intelligence_level": "基础",
            "site_conditions": knowledge["delivery"]["site_conditions"],
        },
        "data_source_note": demo["data_source_note"],
        "knowledge": knowledge,
        "configuration": configuration.get("generated_plan"),
        "delivery": delivery.get("generated_checklist"),
        "disclaimer": demo["disclaimer"],
    }


@router.post("/chat")
async def chat_with_agent(request: dict, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    try:
        message = request.get("message", "")
        user_msg = Conversation(user_id=user_id, role="user", content=message,
                                project_id=request.get("project_id"), session_id=str(user_id))
        db.add(user_msg); await db.commit()
        project_type, _ = detect_project_type(message)
        logger.info("检测到项目类型: %s", project_type)
        if project_type == "delivery_planning":
            context = request.get("context", {}) or {}
            result = await run_moving_agent(
                user_id=user_id,
                user_message=message,
                context={"confirmed_configuration": context.get("configuration") or context},
            )
        else:
            result = await run_renovating_agent(user_id=user_id, user_message=message, context=request.get("context", {}))
        assistant_msg = Conversation(user_id=user_id, role="assistant", content=result.get("response", ""),
            project_id=request.get("project_id"), session_id=str(user_id),
            metadata_={"intent": result.get("intent"), "project_type": project_type,
                       "suggested_actions": result.get("suggested_actions", [])})
        db.add(assistant_msg); await db.commit()
        generated_delivery = result.get("generated_checklist")
        return {
            "message": result.get("response", ""),
            "intent": result.get("intent"),
            "agent": "delivery_planning" if project_type == "delivery_planning" else "space_configuration",
            "project_type": project_type,
            "generated_checklist": generated_delivery,
            "generated_delivery": generated_delivery,
            "generated_plan": result.get("generated_plan"),
            "generation_mode": result.get("generation_mode"),
            "llm_provider": result.get("llm_provider"),
            "suggested_actions": result.get("suggested_actions", []),
        }
    except Exception as e:
        logger.error(f"❌ Agent 处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_chat_history(limit: int = 20, offset: int = 0, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    query = select(Conversation).where(Conversation.user_id == user_id)
    query = query.order_by(desc(Conversation.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    messages = result.scalars().all()
    return {"messages": [{"id": str(msg.id), "role": msg.role, "content": msg.content,
                          "timestamp": msg.created_at.isoformat() if msg.created_at else "",
                          "metadata": msg.metadata_ or {}} for msg in reversed(messages)],
            "total": len(messages)}


@router.delete("/history")
async def clear_chat_history(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    result = await db.execute(select(Conversation).where(Conversation.user_id == user_id))
    messages = result.scalars().all()
    count = len(messages)
    for msg in messages: await db.delete(msg)
    await db.commit()
    return {"message": f"已清除 {count} 条对话记录"}


@router.post("/save-to-project")
async def save_to_project(request: dict, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    project_id = request.get("project_id")
    generated_data = request.get("generated_data", {})
    configuration = generated_data.get("configuration") or generated_data.get("generated_plan") or {}
    delivery = generated_data.get("delivery") or generated_data.get("generated_delivery") or generated_data.get("generated_checklist") or {}
    if not project_id:
        title = configuration.get("project_name") or delivery.get("project_name") or generated_data.get("title") or "卡素民宿配置项目"
        project = Project(
            user_id=user_id,
            title=title,
            project_type=generated_data.get("project_type", "capsule_cabin_demo"),
            requirements={
                "configuration": configuration,
                "delivery": delivery,
                "data_source_note": configuration.get("data_source_note") or delivery.get("data_source_note"),
                "disclaimer": configuration.get("disclaimer") or delivery.get("disclaimer"),
            },
            house_area=configuration.get("recommended_area_sqm"),
            style=configuration.get("style"),
        )
        db.add(project); await db.flush(); project_id = project.id
    else:
        result = await db.execute(select(Project).where(Project.id == project_id).where(Project.user_id == user_id))
        project = result.scalar_one_or_none()
        if not project: raise HTTPException(status_code=404, detail="项目不存在")
        project.requirements = {
            **(project.requirements or {}),
            "configuration": configuration or (project.requirements or {}).get("configuration"),
            "delivery": delivery or (project.requirements or {}).get("delivery"),
        }
        if configuration.get("recommended_area_sqm"):
            project.house_area = configuration.get("recommended_area_sqm")

    if configuration.get("configuration_items"):
        checklist = Checklist(project_id=project_id, checklist_type="configuration_items", name="AI生成的配置清单")
        db.add(checklist); await db.flush()
        for idx, item_name in enumerate(configuration.get("configuration_items", [])):
            item = ChecklistItem(
                checklist_id=checklist.id,
                name=str(item_name),
                category="空间配置",
                quantity=1,
                pack_order=idx + 1,
            )
            db.add(item); checklist.total_items += 1
    if configuration.get("budget_range"):
        budget = Budget(
            project_id=project_id,
            category="示例配置预算",
            item_name=configuration["budget_range"].get("level", "中档配置层级"),
            specifications=configuration["budget_range"].get("note", "示例配置预算区间，不构成正式报价。"),
            planned_amount=0,
            notes="PoC 仅保留预算层级，不保存真实报价。",
        )
        db.add(budget)
    for idx, phase_data in enumerate(delivery.get("delivery_phases", [])):
        db.add(Phase(
            project_id=project_id,
            name=phase_data.get("phase", f"交付阶段 {idx + 1}"),
            order_index=idx + 1,
            tasks=phase_data.get("tasks", []),
            checkpoints=phase_data.get("acceptance_criteria", []),
            notes="；".join(phase_data.get("risks", [])),
        ))
    await db.commit()
    return {"message": "已保存到项目", "project_id": str(project_id)}
