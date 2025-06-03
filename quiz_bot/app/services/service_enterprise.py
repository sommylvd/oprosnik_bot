from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_enterprise as crud
from app.db.schemas.enterprise import EnterpriseCreate
from app.db.models import Enterprises # TODO потом поменять импорт из category

async def create(session: AsyncSession, data: EnterpriseCreate)-> Enterprises | object:
    return await crud.create(session, data)

async def get(session: AsyncSession, enterprise_id: int) ->  Enterprises | object:
    return await crud.get(session, enterprise_id)

async def get_all(session: AsyncSession) -> list[Enterprises] | object:
    return await crud.get_all(session)
