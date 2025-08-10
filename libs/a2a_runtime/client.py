import logging

from typing import List

import httpx

from a2a.types import AgentCard
from openai import BaseModel

from libs.conf import settings

logger = logging.getLogger(__name__)


class AgentDesc(BaseModel):
    namespace: str
    name: str
    card: AgentCard | None = None

    @property
    def description(self) -> str:
        return self.card.description if self.card else ""


async def list_agents(url: str = settings.A2A_RUNTIME_ENDPOINT) -> List[AgentDesc]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return [AgentDesc(**item) for item in data]
        except Exception as e:
            logger.error(f"list agents failed, url: {url}", exc_info=e)
            raise e

