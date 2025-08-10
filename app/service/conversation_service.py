from app.crud.crud_conversation import CRUDConversation
from app.crud.crud_message import CRUDMessage
from app.do.coversation_do import ConversationDO
from app.do.message_do import MessageDO
from libs.database.database import Database


class ConversationService:
    def __init__(self, db: Database, conversation_dao: CRUDConversation, message_dao: CRUDMessage, ):
        self.db = db
        self.conversation_dao = conversation_dao
        self.message_dao = message_dao

    async def create_or_get(self, conversation_id: str | None = None) -> ConversationDO:
        async with self.db.transaction() as session:
            if conversation_id:
                conversation_model = await self.conversation_dao.select_model_by_id(session, conversation_id)
                if conversation_model:
                    message_list = await self.message_dao.recent_list(session, conversation_id)
                    conversation_do = ConversationDO.from_orm(conversation_model)
                    conversation_do.messages = [MessageDO.from_orm(message_model) for message_model in message_list]
                    return conversation_do
            conversation_do = ConversationDO(name="新会话")
            await self.conversation_dao.create_model(session, conversation_do)
        return conversation_do

