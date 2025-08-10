from typing import List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agent.model import Message, MessageRole


def to_lc_message(message: Message) -> BaseMessage:
    if message.role == MessageRole.USER:
        return HumanMessage(content=message.content)
    elif message.role == MessageRole.ASSISTANT:
        return AIMessage(content=message.content)
    else:
        raise ValueError(f'Unknown message role {message.role}')


def to_lc_messages(messages: List[Message] | None) -> List[BaseMessage] | None:
    if not messages:
        return None
    return [to_lc_message(message) for message in messages]
