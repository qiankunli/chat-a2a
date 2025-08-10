from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(default=..., description="用户问题")
    conversation_id: str | None = Field(default=None, description="所属会话, 为空时自动新增")


class StopChatRequest(BaseModel):
    message_id: str = Field(default=..., description="任务id")
