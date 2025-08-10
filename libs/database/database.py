import contextlib
import logging

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from libs.conf import settings

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(
            db_url,
            echo=settings.DB_ECHO,
            future=True,
            pool_size=50,
            pool_recycle=3600,
            pool_pre_ping=True,  # 是否在使用连接前先进行ping, https://docs.sqlalchemy.org/en/14/core/pooling.html#pool-disconnects
            max_overflow=100,
            pool_timeout=20,
        )
        self._session_factory = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            class_=AsyncSession,
            bind=self._engine,
        )

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @contextlib.asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for transactional operations.
        Automatically handles commit/rollback.
        """

        session: AsyncSession = self._session_factory()
        logger.debug(f"Created transaction session: {id(session)}")

        try:
            # 开始事务
            if not session.in_transaction():
                await session.begin()
            try:
                yield session
                # 如果没有异常，提交事务
                await session.commit()
            except Exception as e:
                # 如果有异常，回滚事务
                await session.rollback()
                logger.error(f"Rolled back transaction {id(session)}: {str(e)}")
                raise
        finally:
            # 确保session总是被关闭
            await session.close()
