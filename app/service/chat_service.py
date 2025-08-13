import logging

from collections import defaultdict
from typing import AsyncGenerator

from agent.gate_agent.factory import get_gate_agent
from agent.gate_event import (
    AgentEndEvent,
    AgentInputRequiredEvent,
    AnswerEndEvent,
    AnswerEvent,
    EndEvent,
    ErrorEvent,
    Event,
    HeaderEvent,
    MessageEvent,
    StartEvent,
)
from agent.model import GateAgentConfig, GateContext, UserRequest
from agent.remote_agent.a2a.config import A2AConfig
from app.schema.chat_schema import ChatRequest
from app.service.conversation_service import ConversationService
from app.service.message_service import MessageService
from libs.a2a_runtime.client import list_agents
from libs.database.database import Database
from pkg.llm.factory import get_llm
from utils.str import uuid7_hex

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: Database, conversation_service: ConversationService,
                 message_service: MessageService,
                 ):
        self.db = db
        self.conversation_service = conversation_service
        self.message_service = message_service

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[Event, None]:
        conversation = await self.conversation_service.create_or_get(request.conversation_id)
        # 如果存在 input_required，则复用input_required message 对应的intention_id
        # （下游对应的agent 还处于input_required 状态）
        intention_id = conversation.current_intention_id or uuid7_hex()
        gate_agent = get_gate_agent(GateAgentConfig(llm=get_llm()))
        agent_desc_list = await list_agents()
        logger.info(f"find {len(agent_desc_list)} agents, start to chat")
        # 如果存在 input_required，则汇总同intention_id 下的agent 执行记录，便于plan理解用户最新query
        agent_history = conversation.agent_history(intention_id)
        context = GateContext(conversation_id=conversation.id, intention_id=intention_id,
                              chat_history=conversation.chat_history,
                              agent_history=agent_history,
                              agent_configs=[A2AConfig.from_agent_desc(agent_desc) for agent_desc in agent_desc_list])
        logger.info(f"try chat query {request.query},intention_id {intention_id}, "
                    f"agent_history {agent_history} in conversation {conversation.id}")
        user_request = UserRequest(query=request.query)
        await self.message_service.add_user(conversation.id, intention_id, request.query)

        async def response_stream() -> AsyncGenerator[Event, None]:
            yield StartEvent(conversation_id=conversation.id, intention_id=intention_id)
            group_stream_content: dict[str, str] = defaultdict(str)
            answer = ''
            try:
                async for evt in gate_agent.astream_event(context, user_request):
                    if isinstance(evt, MessageEvent):
                        group_stream_content[evt.name] += evt.chunk
                    elif isinstance(evt, HeaderEvent):
                        await self.message_service.add_agent_query(conversation.id, intention_id,
                                                                   query=evt.chunk,
                                                                   from_agent=evt.name)
                    elif isinstance(evt, AnswerEvent):
                        answer += evt.chunk
                    elif isinstance(evt, AgentEndEvent):
                        await self.message_service.add_agent_answer(conversation.id, intention_id,
                                                                    answer=group_stream_content[evt.name],
                                                                    from_agent=evt.name)
                    elif isinstance(evt, AgentInputRequiredEvent):
                        await self.message_service.add_agent_input_required(conversation.id, intention_id,
                                                                            require_input=evt.require_input,
                                                                            from_agent=evt.name)
                    elif isinstance(evt, AgentEndEvent):
                        await self.message_service.add_agent_error(conversation.id, intention_id,
                                                                   from_agent=evt.name)
                    elif isinstance(evt, AnswerEndEvent):
                        await self.message_service.add_answer(conversation.id, intention_id, answer=answer)
                    yield evt
            except Exception as e:
                logger.error(f"handle query {request.query} error ", exc_info=e)
                yield ErrorEvent(error=str(e))
            finally:
                yield EndEvent()

        return response_stream()
