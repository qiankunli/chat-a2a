from abc import ABC, abstractmethod
from typing import List

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from agent.model import CallAgent, GateContext, UserRequest


class PlanNext(BaseModel):
    query: str = Field(description="下一步要调用该 Agent 时的查询语句（使用主谓宾完整表达）")
    agent_name: str = Field(description="下一步要调用的Agent 名称")
    end: bool = Field(False, description="是否结束任务（true/false）")
    reason: str | None = Field(None, description="选择该 Agent 的原因（可选）")


class BasePlanner(ABC):
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    @abstractmethod
    def plan(self, context: GateContext, user_request: UserRequest, call_agents: List[CallAgent]) -> PlanNext:
        pass
