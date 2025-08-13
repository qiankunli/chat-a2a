from enum import Enum
from typing import Any, Dict, List

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel


class MessageRole(str, Enum):
    USER = 'user'
    ASSISTANT = 'assistant'
    AGENT = 'agent'


class MessageType(str, Enum):
    QUERY = 'query'
    ANSWER = 'answer'
    INPUT_REQUIRED = 'input_required'
    ERROR = 'error'


class Message(BaseModel):
    content: str
    role: MessageRole

    @classmethod
    def create(cls, content: str, role: str | MessageRole) -> "Message":
        if isinstance(role, str):
            role = MessageRole(role)
        return cls(content=content, role=role)


class SendMessage(Message):
    metadata: Dict[str, Any] | None = None


class StreamMessage(Message):
    type: MessageType | None = None


class UserRequest(BaseModel):
    """gate agent问答时用户的最新请求"""

    query: str


class AgentConfig(BaseModel):
    name: str
    description: str


class LocalAgentConfig(AgentConfig):
    pass


class RemoteAgentConfig(AgentConfig):
    pass


class CallAgent(BaseModel):
    """ 记录一次agent调用"""
    name: str
    query: str
    answer: str | None = None
    reason: str | None = None


class GateContext(BaseModel):
    """gate agent问答所需的上下文，问答时确定，但与用户最新请求无关"""
    conversation_id: str
    intention_id: str
    # 用户聊天历史记录
    chat_history: List[Message] | None
    # agent执行记录
    agent_history: List[Message] | None
    # 本次问答的候选agent 列表
    agent_configs: List[AgentConfig]

    def get_agent_config(self, agent_name: str) -> AgentConfig:
        for agent_config in self.agent_configs:
            if agent_config.name == agent_name:
                return agent_config
        raise ValueError(f'agent {agent_name} not found')


class GateAgentConfig(BaseModel):
    """gate agent 基础配置，构建agent 时即确定"""
    llm: BaseChatModel

