from pydantic import Field

from agent.model import Message, MessageRole, MessageType
from app.do.base import DOAttributeBase
from app.model.message_po import MessageModel
from utils.str import uuid7_hex


class MessageDO(DOAttributeBase):
    # 插入时id 不作数，只是查询时需要
    id: str = Field(default_factory=uuid7_hex)
    conversation_id: str
    task_id: str
    role: MessageRole = MessageRole.USER
    content: str | None = None
    type: MessageType | None = None
    agent: str | None = None

    def do_to_model(self, **kwargs):
        model = MessageModel(**self.model_dump(), **kwargs)
        # 如果用枚举类，则do_to_model 要注意
        model.role = self.role.value
        if self.type:
            model.type = self.type.value
        return model

    @property
    def agent_message(self) -> Message:
        return Message(role=MessageRole(self.role), content=self.content)
