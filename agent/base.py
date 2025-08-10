from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

from agent.gate_event import Event
from agent.model import (
    AgentConfig,
    GateAgentConfig,
    GateContext,
    RemoteAgentConfig,
    SendMessage,
    StreamMessage,
    UserRequest,
)


class BaseGateAgent(ABC):
    """
    与常规Agent不同的是，该Agent面向用户，输出不是文本，而是Event
    """
    name: str

    def __init__(self, name: str, config: GateAgentConfig, ):
        self.name = name
        self.config = config

    @abstractmethod
    async def astream_event(
            self,
            gate_context: GateContext,
            user_request: UserRequest,
    ) -> AsyncGenerator[Event, None]:
        pass


class BaseAgent(ABC):
    """基础Agent，负责处理消息"""

    def __init__(self, config: AgentConfig, ):
        self.config = config

    @abstractmethod
    async def arun(
            self,
            gate_context: GateContext,
            message: SendMessage,
            metadata: dict[str, Any] | None = None
    ) -> AsyncGenerator[StreamMessage, None]:
        pass


class RemoteAgent(BaseAgent):
    def __init__(self, config: RemoteAgentConfig, ):
        super().__init__(config)

    @abstractmethod
    async def arun(
            self,
            gate_context: GateContext,
            message: SendMessage,
            metadata: dict[str, Any] | None = None
    ) -> AsyncGenerator[StreamMessage, None]:
        pass


