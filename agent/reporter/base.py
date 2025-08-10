from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from langchain_core.language_models import BaseChatModel

from agent.model import GateContext, Message, UserRequest


class BaseReporter(ABC):
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    @abstractmethod
    async def report(self, context: GateContext, user_request: UserRequest,
                     messages: List[Message]) -> AsyncGenerator[str, None]:
        pass
