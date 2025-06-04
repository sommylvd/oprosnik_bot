from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_enterprise as crud
from app.db.schemas.enterprise import EnterpriseCreate
from app.db.models import Enterprises

async def create(session: AsyncSession, data: EnterpriseCreate)-> Enterprises | object:
    """
    Создает новое предприятие в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (EnterpriseCreate): Данные для создания предприятия.

    Returns:
        Enterprises | list: Объект предприятия или пустой список при ошибке.
    """
    return await crud.create(session, data)

async def get(session: AsyncSession, enterprise_id: int) ->  Enterprises | object:
    """
    Получает предприятие по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        enterprise_id (int): Идентификатор предприятия.

    Returns:
        Enterprises | None: Объект предприятия или None при отсутствии/ошибке.
    """
    return await crud.get(session, enterprise_id)

async def get_all(session: AsyncSession) -> list[Enterprises] | object:
    """
    Получает все предприятия из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.

    Returns:
        list[Enterprises] | list: Список предприятий или пустой список при ошибке.
    """
    return await crud.get_all(session)
