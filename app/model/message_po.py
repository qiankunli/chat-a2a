from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from common.model import Base, id_key
from utils.str import uuid7_hex


class MessageModel(Base):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return 'message'

    id: Mapped[id_key] = mapped_column(String(36), primary_key=True, default_factory=uuid7_hex)
    conversation_id: Mapped[str] = mapped_column(String(36), default=None, nullable=False, comment='会话id')
    intention_id: Mapped[str] = mapped_column(String(36), default=None, nullable=False, comment='意图id')
    role: Mapped[str] = mapped_column(String(36), default=None, comment="角色")
    type: Mapped[str | None] = mapped_column(String(36), default=None, comment="消息类型")
    content: Mapped[str] = mapped_column(Text, default=None, comment="内容")
    agent: Mapped[str | None] = mapped_column(String(128), default=None, comment="agent名称")
