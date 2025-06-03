from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db import models
from app.core.config import config

async_engine = create_async_engine(config.database_url, echo=config.ECHO)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all) 


async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all) 
        

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def main():
    await init_db()
    