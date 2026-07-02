"""数据库连接和会话管理模块"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from typing import AsyncGenerator

try:
    from sqlalchemy.ext.asyncio import async_sessionmaker
except ImportError:  # SQLAlchemy 1.4 兼容
    async_sessionmaker = None

try:
    from sqlalchemy.orm import DeclarativeBase
except ImportError:  # SQLAlchemy 1.4 兼容
    DeclarativeBase = None
    from sqlalchemy.ext.declarative import declarative_base

settings = get_settings()

engine_options = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}

if not settings.DATABASE_URL.startswith("sqlite"):
    engine_options.update({"pool_size": 10, "max_overflow": 20})

engine = create_async_engine(settings.DATABASE_URL, **engine_options)

session_factory = async_sessionmaker or sessionmaker
AsyncSessionLocal = session_factory(engine, class_=AsyncSession, expire_on_commit=False)


if DeclarativeBase is not None:
    class Base(DeclarativeBase):
        """ORM 基类"""
        pass
else:
    Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖注入"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库 - 创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("数据库表创建完成")


async def drop_db():
    """删除所有表 - 慎用!"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("所有表已删除")
