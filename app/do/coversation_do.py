from typing import List

from pydantic import Field

from agent.model import Message, MessageRole, MessageType, CallAgent
from app.do.base import DOAttributeBase
from app.do.message_do import MessageDO
from app.model.conversation_po import ConversationModel
from utils.str import uuid7_hex


class ConversationDO(DOAttributeBase):
    id: str = Field(default_factory=uuid7_hex)
    name: str
    introduction: str | None = None
    # 假设创建时间降序
    messages: List[MessageDO] | None = None

    def do_to_model(self, **kwargs):
        return ConversationModel(id=self.id, name=self.name, introduction=self.introduction)

    @property
    def chat_history(self) -> List[Message]:
        if not self.messages:
            return []
        # agent 中间输出不作为聊天记录
        return [message.agent_message for message in self.messages if
                message.role in [MessageRole.USER, MessageRole.ASSISTANT]]

    @property
    def input_required_task_id(self) -> str | None:
        if not self.messages:
            return None
        task_id = None
        # 寻找反问且未得到解答的的task_id
        for message in self.messages:
            if message.type == MessageType.INPUT_REQUIRED:
                task_id = message.task_id
            if message.role == MessageRole.ASSISTANT:
                # 该task_id 关联的问题已得到解答
                if task_id and task_id == message.task_id:
                    task_id = None
        return task_id

    def agent_history(self, task_id: str) -> List[Message] | None:
        if not self.messages:
            return None
        task_id = None
        ret = []
        # 寻找反问且未得到解答的的task_id
        for message in self.messages:
            if message.task_id != task_id:
                continue
            if message.role != MessageRole.AGENT:
                continue
            ret.append(message.agent_message)
        return ret
