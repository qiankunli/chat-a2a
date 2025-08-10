from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict

from langchain_core.runnables import Runnable

from agent.base import BaseGateAgent
from agent.gate_agent.langgraph.event import LCEventType
from agent.gate_event import AgentEndEvent, AnswerEndEvent, AnswerEvent, Event, EventType, HeaderEvent, MessageEvent, \
    AgentInputRequiredEvent, AgentErrorEvent
from agent.model import GateAgentConfig, GateContext, UserRequest


@dataclass
class ContextSchema:
    context: GateContext


class BaseLGGateAgent(BaseGateAgent):
    chain: Runnable

    def __init__(self, name: str, config: GateAgentConfig) -> None:
        super().__init__(name, config)

    @abstractmethod
    def _build_graph(self):
        pass

    def _build_input(self, context: GateContext,
                     request: UserRequest, ) -> Dict[str, Any]:
        return {"user_request": request}

    async def astream_event(
            self,
            gate_context: GateContext,
            user_request: UserRequest,
    ) -> AsyncGenerator[Event, None]:
        input_ = self._build_input(gate_context, user_request)
        response = self.chain.astream_events(input_, context={"gate_context": gate_context}, version="v2", )
        # 将框架event 转为gate event
        async for event in response:
            kind = event.get("event")
            if kind == LCEventType.CUSTOM_EVENT:
                event_detail = event.get("data")
                if event.get("name") == EventType.HEADER:
                    yield HeaderEvent(chunk=event_detail.content, name=event_detail.from_agent)
                elif event.get("name") == EventType.MESSAGE:
                    yield MessageEvent(chunk=event_detail.content, name=event_detail.from_agent)
                elif event.get("name") == EventType.Agent_END:
                    yield AgentEndEvent(name=event_detail.from_agent)
                elif event.get("name") == EventType.AGENT_INPUT_REQUIRED:
                    yield AgentInputRequiredEvent(require_input=event_detail.content, name=event_detail.from_agent)
                elif event.get("name") == EventType.AGENT_ERROR:
                    yield AgentErrorEvent(name=event_detail.from_agent)
                elif event.get("name") == EventType.ANSWER:
                    yield AnswerEvent(chunk=event_detail.content)
                elif event.get("name") == EventType.ANSWER_END:
                    yield AnswerEndEvent()
