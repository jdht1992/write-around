from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.config import settings

# --- POOLING ASÍNCRONO POSTGRES ---
"""
Opening a connection = expensive (TCP handshake, authentication, memory allocation)
Closing it every request = slow
So we reuse them → Connection Pool
"""
engine = create_async_engine(
    settings.async_database_url,
    echo=True,            # Enable SQL query logging
    future=True,          # Use SQLAlchemy 2.0 style
    pool_pre_ping=True,   # Enable connection pool pre-ping
    pool_size=10,         # Set the connection pool size
    max_overflow=20,      # Set the maximum number of overflow connections
    pool_timeout=30,      # Set the connection timeout in seconds
    pool_recycle=1800,    # Set the connection recycle time in seconds
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
