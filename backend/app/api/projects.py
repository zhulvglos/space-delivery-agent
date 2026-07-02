"""项目 API 模块"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.database import get_db
from app.models.project import Project, Checklist, ChecklistItem, Budget, Phase

router = APIRouter(prefix="/api/v1/projects")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


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


@router.get("")
async def list_projects(project_type: str = None, status: str = None, skip: int = 0, limit: int = 20,
                        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    query = select(Project).where(Project.user_id == user_id)
    if project_type: query = query.where(Project.project_type == project_type)
    if status: query = query.where(Project.status == status)
    query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    projects = result.scalars().all()
    return [{"id": str(p.id), "title": p.title, "project_type": p.project_type, "status": p.status,
             "requirements": p.requirements or {}, "total_budget": p.total_budget,
             "created_at": p.created_at.isoformat() if p.created_at else None}
            for p in projects]


@router.post("")
async def create_project(data: dict, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    project = Project(user_id=user_id, title=data.get("title", "新项目"),
        project_type=data.get("project_type", "capsule_cabin_demo"),
        requirements=data.get("requirements", {}),
        source_address=data.get("source_address"), target_address=data.get("target_address"),
        moving_date=data.get("moving_date"), mover_count=data.get("mover_count", 2),
        house_type=data.get("house_type"), house_area=data.get("house_area"),
        current_state=data.get("current_state", "毛坯"), style=data.get("style", "现代简约"),
        total_budget=data.get("total_budget", 0))
    db.add(project); await db.commit(); await db.refresh(project)
    return {"id": str(project.id), "title": project.title, "project_type": project.project_type}


@router.get("/{project_id}")
async def get_project(project_id: UUID, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    result = await db.execute(select(Project)
        .options(selectinload(Project.checklists).selectinload(Checklist.items))
        .options(selectinload(Project.budgets))
        .options(selectinload(Project.phases))
        .where(Project.id == project_id)
        .where(Project.user_id == user_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    requirements = project.requirements or {}
    return {
        "id": str(project.id),
        "title": project.title,
        "project_type": project.project_type,
        "status": project.status,
        "requirements": requirements,
        "configuration": requirements.get("configuration"),
        "delivery": requirements.get("delivery"),
        "data_source_note": requirements.get("data_source_note"),
        "disclaimer": requirements.get("disclaimer"),
        "source_address": project.source_address,
        "target_address": project.target_address,
        "house_type": project.house_type,
        "house_area": project.house_area,
        "style": project.style,
        "total_budget": project.total_budget,
        "checklists": [{
            "id": str(c.id),
            "name": c.name,
            "checklist_type": c.checklist_type,
            "total_items": c.total_items,
            "completed_items": c.completed_items,
            "progress": c.progress,
            "items": [{"id": str(i.id), "name": i.name, "category": i.category, "quantity": i.quantity} for i in c.items],
        } for c in project.checklists],
        "budgets": [{
            "id": str(b.id),
            "category": b.category,
            "item_name": b.item_name,
            "specifications": b.specifications,
            "planned_amount": b.planned_amount,
            "notes": b.notes,
        } for b in project.budgets],
        "phases": [{
            "id": str(p.id),
            "name": p.name,
            "order_index": p.order_index,
            "tasks": p.tasks,
            "checkpoints": p.checkpoints,
            "notes": p.notes,
            "status": p.status,
        } for p in sorted(project.phases, key=lambda item: item.order_index)],
    }


@router.put("/{project_id}")
async def update_project(project_id: UUID, data: dict, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    result = await db.execute(select(Project).where(Project.id == project_id).where(Project.user_id == user_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    for key, value in data.items():
        if hasattr(project, key) and key not in ("id", "user_id", "created_at"):
            setattr(project, key, value)
    await db.commit(); await db.refresh(project)
    return {"id": str(project.id), "title": project.title, "project_type": project.project_type}


@router.delete("/{project_id}")
async def delete_project(project_id: UUID, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    result = await db.execute(select(Project).where(Project.id == project_id).where(Project.user_id == user_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    await db.delete(project); await db.commit()
