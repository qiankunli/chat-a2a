#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Type

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.util import AliasedClass

from pkg.acrud_plus.types import Model


async def count(
    session: AsyncSession,
    model: Type[Model] | AliasedClass,
    filters: list[ColumnElement],
) -> int:
    """
    Counts records that match specified filters.

    :param session: The sqlalchemy session to use for the operation.
    :param model: The SQLAlchemy model.
    :param filters: Filters to apply for the count.
    :return:
    """
    stmt = select(func.count()).select_from(model)
    if filters:
        stmt = stmt.where(*filters)
    query = await session.execute(stmt)
    total_count = query.scalar()
    return total_count if total_count is not None else 0
