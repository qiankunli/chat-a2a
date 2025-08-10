#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.message_po import MessageModel
from pkg.acrud_plus.crud import ACRUDPlus


class CRUDMessage(ACRUDPlus[MessageModel]):
    def __init__(self):
        super().__init__(MessageModel)

    async def recent_list(self, session: AsyncSession, conversation_id: str,
                          limit: int = 10, ) -> Sequence[MessageModel]:
        # 所谓最近的，检索的时候只能倒排。create_time 时间精度不够，所以按id
        from agent.model import MessageRole
        query = (select(self.model).filter(MessageModel.conversation_id == conversation_id)
                 .order_by(MessageModel.id.desc())
                 .limit(limit)
                 )

        result = await session.execute(query)
        return result.scalars().all()
