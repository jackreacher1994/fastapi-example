import functools
import logging

from contextvars import ContextVar
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import Any, Awaitable, Callable

from config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.database_url)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

db_session_ctx: ContextVar[AsyncSession] = ContextVar("db_session_ctx")
root_transaction_ctx: ContextVar[bool] = ContextVar("root_transaction_ctx", default=False)

def get_current_session() -> AsyncSession:
    session = db_session_ctx.get()
    if not session:
        raise RuntimeError("No active DB session found")
    return session

def get_db_session_context() -> str:
    return f"session_id={id(get_current_session())}"

AsyncCallable = Callable[..., Awaitable[Any]]

def transactional(func: AsyncCallable) -> AsyncCallable:
    @functools.wraps(func)
    async def _wrapper(*args, **kwargs) -> Awaitable[Any]:
        db_session = get_current_session()

        # Root transaction context check
        is_root_tx = not root_transaction_ctx.get()
        token = None

        try:
            if is_root_tx:
                # Handle implicit transaction
                if db_session.in_transaction():
                    logger.debug(
                        "Rolling back implicit transaction before starting explicit one."
                    )
                    await db_session.rollback()

                token = root_transaction_ctx.set(True)

                async with db_session.begin():
                    result = await func(*args, **kwargs)
                # if result:
                #     await db_session.refresh(result)
            else:
                # Nested call, reuse current session
                result = await func(*args, **kwargs)

            return result

        except Exception as error:
            logger.info(f"request hash: {get_db_session_context()}")
            logger.exception(error)
            raise
        finally:
            if is_root_tx and token is not None:
                root_transaction_ctx.reset(token)

    return _wrapper

async def get_session():
    async with session_factory() as session:
        token = db_session_ctx.set(session)
        try:
            yield session
        finally:
            db_session_ctx.reset(token)