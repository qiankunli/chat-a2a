# 定义一个协议，确保所有的模型都有一个 'id' 属性
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Mapped


class HasId(Protocol):
    # 可能是int 也可能是str
    id: Mapped[Any]


Model = TypeVar("Model", bound=HasId)

CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)
