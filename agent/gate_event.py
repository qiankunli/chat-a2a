from enum import Enum

from pydantic import BaseModel


class EventType(str, Enum):
    """ 不同的类型，前端可以用来做渲染"""
    START = "start"
    HEADER = "header"
    MESSAGE = "message"
    Agent_END = "agent_end"
    AGENT_INPUT_REQUIRED = "agent_input_required"
    AGENT_ERROR = "agent_error"
    # 最终结果特殊标记下，与header/message 区分
    ANSWER = "answer"
    ANSWER_END = "answer_end"

    ERROR = "error"
    STOP = "stop"
    PING = "ping"
    END = "end"


class Event(BaseModel):
    event: EventType


class StartEvent(Event):
    event: EventType = EventType.START
    conversation_id: str
    task_id: str


class EndEvent(Event):
    event: EventType = EventType.END


class AgentEvent(Event):
    """某个Agent的event"""
    name: str


class HeaderEvent(AgentEvent):
    """一般用于输入子问题、中间问题等"""
    event: EventType = EventType.HEADER
    chunk: str


class MessageEvent(AgentEvent):
    """一般用于输出子问题答案"""
    event: EventType = EventType.MESSAGE
    chunk: str


class AgentEndEvent(AgentEvent):
    """标记agent 输出结束，便于后端保存，前端换行"""
    event: EventType = EventType.Agent_END


class AgentInputRequiredEvent(AgentEvent):
    event: EventType = EventType.AGENT_INPUT_REQUIRED
    require_input: str


class AgentErrorEvent(AgentEvent):
    event: EventType = EventType.AGENT_ERROR


class StopEvent(Event):
    event: EventType = EventType.STOP


class PingEvent(Event):
    event: EventType = EventType.PING


class ErrorEvent(Event):
    event: EventType = EventType.ERROR
    error: str


class AnswerEvent(Event):
    """一般用于输出最终答案"""
    event: EventType = EventType.ANSWER
    chunk: str


class AnswerEndEvent(Event):
    event: EventType = EventType.ANSWER_END
