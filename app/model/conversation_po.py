
from sqlalchemy import String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from common.model import Base, id_key
from utils.str import uuid7_hex


class ConversationModel(Base):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return 'conversation'

    id: Mapped[id_key] = mapped_column(String(36), primary_key=True, default_factory=uuid7_hex)
    name: Mapped[str | None] = mapped_column(String(255), default=None, index=True, comment='名称')
    introduction: Mapped[str | None] = mapped_column(String(255), default=None, comment="简介")
