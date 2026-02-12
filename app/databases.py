from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/write_around_db"

# --- POOLING ASÍNCRONO POSTGRES ---
"""
Opening a connection = expensive (TCP handshake, authentication, memory allocation)
Closing it every request = slow
So we reuse them → Connection Pool
"""
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    #echo=True,
    echo_pool=True,
    pool_recycle=1800,
)

# Create singleton async sessionmaker instance
async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

async def create_all_tables() -> None:
    """
    Creates the database and tables defined in the SQLModel metadata.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    If you don't close the session, connection never returns to the pool, 
    and you can run out of connections.
    """
    async with async_session() as session:
        yield session
