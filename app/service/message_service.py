from typing import List

from agent.model import MessageRole, MessageType
from app.crud.crud_message import CRUDMessage
from app.do.message_do import MessageDO
from libs.database.database import Database


class MessageService:
    def __init__(self, db: Database, message_dao: CRUDMessage, ):
        self.db = db
        self.message_dao = message_dao

    async def recent_list(self, conversation_id: str, limit: int = 10, ) -> List[MessageDO]:
        async with self.db.session() as session:
            message_models = await self.message_dao.recent_list(session, conversation_id, limit=limit, )
            # 确保返回的message 按时间asc，content 为空的不算
            message_dos = []
            for message_model in reversed(message_models):
                if message_model.content:
                    message_dos.append(MessageDO.from_orm(message_model))
            return message_dos

    async def add_user(self, conversation_id: str, intention_id: str, query: str) -> None:
        async with self.db.transaction() as session:
            user_message_do = MessageDO(conversation_id=conversation_id,
                                        intention_id=intention_id,
                                        role=MessageRole.USER,
                                        content=query)
            await self.message_dao.create_model(session, user_message_do)

    async def add_agent_query(self, conversation_id: str, intention_id: str, query: str, from_agent: str) -> None:
        async with self.db.transaction() as session:
            user_message_do = MessageDO(conversation_id=conversation_id,
                                        intention_id=intention_id,
                                        role=MessageRole.AGENT,
                                        type=MessageType.QUERY,
                                        content=query, agent=from_agent)
            await self.message_dao.create_model(session, user_message_do)

    async def add_agent_answer(self, conversation_id: str, intention_id: str, answer: str, from_agent: str) -> None:
        async with self.db.transaction() as session:
            user_message_do = MessageDO(conversation_id=conversation_id,
                                        intention_id=intention_id,
                                        role=MessageRole.AGENT,
                                        type=MessageType.ANSWER,
                                        content=answer, agent=from_agent)
            await self.message_dao.create_model(session, user_message_do)

    async def add_agent_error(self, conversation_id: str, intention_id: str, from_agent: str) -> None:
        async with self.db.transaction() as session:
            user_message_do = MessageDO(conversation_id=conversation_id,
                                        intention_id=intention_id,
                                        role=MessageRole.AGENT,
                                        type=MessageType.ERROR,
                                        # todo 得空看能不能把error 记录下来
                                        content='', agent=from_agent)
            await self.message_dao.create_model(session, user_message_do)

    async def add_agent_input_required(self, conversation_id: str, intention_id: str, require_input: str,
                                       from_agent: str) -> None:
        async with self.db.transaction() as session:
            user_message_do = MessageDO(conversation_id=conversation_id,
                                        intention_id=intention_id,
                                        role=MessageRole.AGENT,
                                        type=MessageType.INPUT_REQUIRED,
                                        content=require_input, agent=from_agent)
            await self.message_dao.create_model(session, user_message_do)

    async def add_answer(self, conversation_id: str, intention_id: str, answer: str) -> None:
        async with self.db.transaction() as session:
            user_message_do = MessageDO(conversation_id=conversation_id, intention_id=intention_id,
                                        role=MessageRole.ASSISTANT,
                                        content=answer)
            await self.message_dao.create_model(session, user_message_do)
