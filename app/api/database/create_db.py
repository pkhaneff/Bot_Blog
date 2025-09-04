"""Create database from ORM"""
from app.api.database.models.base import Base, engine
from app.api.database.models import imported_document  

async def create_db():
    """Create Database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
