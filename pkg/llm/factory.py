from langchain_community.chat_models import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from libs.conf import settings


def get_llm(api_base: str = settings.LLM_API_BASE, api_key: str = settings.LLM_API_KEY,
            model: str = settings.LLM_MODEL) -> BaseChatModel:
    # 给出langchain openapi 实现
    return ChatOpenAI(
        model_name=model,
        api_key=api_key,
        base_url=api_base,
    )
