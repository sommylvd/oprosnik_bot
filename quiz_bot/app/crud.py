from .models import Industry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def get_industries(session: AsyncSession):
    result = await session.execute(select(Industry))
    return result.scalars().all()
