import json
import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from agent.gate_event import Event
from app.schema.chat_schema import ChatRequest
from app.service.chat_service import ChatService
from common.container.container import Container
from common.exception.errors import ServerError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def _formatted_sse_data(evt: Event) -> str:
    json_data = json.dumps(evt.model_dump(exclude_none=True), ensure_ascii=False)
    return f"data: {json_data}\n\n"


@router.post("")
@inject
async def chat(chat_request: ChatRequest,
               chat_service: ChatService = Depends(Provide[Container.chat_service]), ):
    try:
        response = await chat_service.stream_chat(chat_request, )

        async def response_stream():
            async for output_evt in response:
                yield _formatted_sse_data(output_evt)

        return StreamingResponse(
            response_stream(),
            media_type="text/event-stream",
        )

    except Exception as e:
        msg = f"聊天出错： {e}"
        logger.exception("An error occurred: %s", e)
        raise ServerError(msg=msg)
