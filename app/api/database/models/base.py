"""Base connect/class for database"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.config import POSTGRES_DETAILS

engine = create_async_engine(url = POSTGRES_DETAILS,
                             echo = True)

session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base Class for classes definitions"""
    pass

async def get_db() -> AsyncSession:
    async with session() as db:
        yield db
