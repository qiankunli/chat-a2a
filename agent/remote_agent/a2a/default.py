import logging

from typing import Any, AsyncGenerator

import httpx

from a2a.client import A2AClient
from a2a.types import (
    JSONRPCErrorResponse,
    MessageSendParams,
    SendStreamingMessageRequest,
    SendStreamingMessageSuccessResponse,
    TaskState,
)

from agent.base import RemoteAgent
from agent.model import GateContext, MessageRole, MessageType, RemoteAgentConfig, SendMessage, StreamMessage
from agent.utils.a2a.message import get_text_from_message_parts
from utils.str import uuid7_hex

logger = logging.getLogger(__name__)


class DefaultAgent(RemoteAgent):
    def __init__(
            self,
            config: RemoteAgentConfig,
    ):
        super().__init__(config)

    async def arun(
            self, gate_context: GateContext, message: SendMessage, metadata: dict[str, Any] | None = None
    ) -> AsyncGenerator[StreamMessage, None]:
        async with httpx.AsyncClient() as httpx_client:
            client = A2AClient(
                httpx_client=httpx_client, agent_card=self.config.card
            )
            send_message_payload: dict[str, Any] = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': message.content}
                    ],
                    "task_id": gate_context.task_id,
                    'message_id': uuid7_hex(),
                    'context_id': gate_context.conversation_id,
                },
            }

            streaming_request = SendStreamingMessageRequest(
                id=uuid7_hex(), params=MessageSendParams(**send_message_payload)
            )
            stream_response = client.send_message_streaming(streaming_request)
            async for chunk in stream_response:
                print(type(chunk))
                print(chunk)
                if isinstance(chunk.root, JSONRPCErrorResponse):
                    yield StreamMessage(content=chunk.root.message, role=MessageRole.AGENT, type=MessageType.ERROR)
                    return
                elif isinstance(chunk.root, SendStreamingMessageSuccessResponse):
                    result = chunk.root.result
                    state, text = get_text_from_message_parts(result)
                    logger.info(f"read state: {state} text: {text} from a2a")
                    if state == TaskState.input_required:
                        yield StreamMessage(content=text, role=MessageRole.AGENT, type=MessageType.INPUT_REQUIRED)
                        return
                    elif state == TaskState.completed:
                        yield StreamMessage(content=text, role=MessageRole.AGENT,)
                        return
                    elif state == TaskState.working:
                        yield StreamMessage(content=text, role=MessageRole.AGENT, )
