"""跨数据库模型类型。"""
from sqlalchemy import CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator
import uuid


class GUID(TypeDecorator):
    """PostgreSQL 使用 UUID，SQLite 等数据库使用 36 位字符串。"""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
