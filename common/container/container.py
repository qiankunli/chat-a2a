from dependency_injector import containers, providers

from app.crud.crud_conversation import CRUDConversation
from app.crud.crud_message import CRUDMessage
from app.service.chat_service import ChatService
from app.service.conversation_service import ConversationService
from app.service.message_service import MessageService
from libs.conf import settings
from libs.database.database import Database


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.chat",
        ]
    )
    # infra
    db = providers.Singleton(Database, db_url=settings.SQLALCHEMY_DATABASE_URL)

    # dao
    message_dao = providers.Singleton(CRUDMessage)
    conversation_dao = providers.Singleton(CRUDConversation)

    # service
    message_service = providers.Singleton(
        MessageService,
        db=db,
        message_dao=message_dao
    )
    conversation_service = providers.Singleton(
        ConversationService,
        db=db,
        conversation_dao=conversation_dao,
        message_dao=message_dao
    )
    chat_service = providers.Singleton(
        ChatService,
        db=db,
        message_service=message_service,
        conversation_service=conversation_service,
    )


