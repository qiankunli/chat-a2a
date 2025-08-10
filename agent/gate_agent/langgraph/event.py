from enum import Enum

from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from agent.gate_event import EventType


class LCEventType(str, Enum):
    CHAT_STREAM = "on_chat_model_stream"
    TOOL_START = "on_tool_start"
    TOOL_END = "on_tool_end"
    CHAIN_STREAM = "on_chain_stream"
    CUSTOM_EVENT = "on_custom_event"


class LCCustomEvent(BaseModel):
    content: str | None = None
    from_agent: str | None = None


async def dispatch_header_event(from_agent: str, content: str, config: RunnableConfig):
    await adispatch_custom_event(
        EventType.HEADER, LCCustomEvent(content=content, from_agent=from_agent), config=config
    )


async def dispatch_message_event(from_agent: str, content: str, config: RunnableConfig):
    await adispatch_custom_event(
        EventType.MESSAGE,
        LCCustomEvent(content=content, from_agent=from_agent),
        config=config,
    )


async def dispatch_agent_end_event(from_agent: str, config: RunnableConfig):
    await adispatch_custom_event(
        EventType.Agent_END,
        LCCustomEvent(from_agent=from_agent),
        config=config,
    )


async def dispatch_input_required_event(from_agent: str, content: str, config: RunnableConfig):
    await adispatch_custom_event(
        EventType.AGENT_INPUT_REQUIRED,
        LCCustomEvent(content=content, from_agent=from_agent),
        config=config,
    )


async def dispatch_agent_error_event(from_agent: str, config: RunnableConfig):
    await adispatch_custom_event(
        EventType.AGENT_ERROR,
        LCCustomEvent(from_agent=from_agent),
        config=config,
    )


async def dispatch_answer_event(answer: str, config: RunnableConfig):
    await adispatch_custom_event(
        EventType.ANSWER,
        LCCustomEvent(content=answer),
        config=config,
    )


async def dispatch_answer_end_event(config: RunnableConfig):
    await adispatch_custom_event(
        EventType.ANSWER_END,
        LCCustomEvent(),
        config=config,
    )
