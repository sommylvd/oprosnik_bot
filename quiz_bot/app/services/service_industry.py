from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_industry as crud
from app.db.schemas.industry import IndustryCreate
from app.db.models import Industries 

async def create(session: AsyncSession, data: IndustryCreate)-> Industries | object:
    """
    Создает новую промышленность в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (IndustryCreate): Данные для создания промышленности.

    Returns:
        Industries | list: Объект промышленности или пустой список при ошибке.
    """
    return await crud.create(session, data)

async def get(session: AsyncSession, industry_id: int) ->  Industries | object:
    """
    Получает промышленность по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        industry_id (int): Идентификатор промышленности.

    Returns:
        Industries | None: Объект промышленности или None при отсутствии/ошибке.
    """
    return await crud.get(session, industry_id)

async def get_all(session: AsyncSession) -> list[Industries] | object:
    """
    Получает все промышленности из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.

    Returns:
        list[Industries] | list: Список промышленностей или пустой список при ошибке.
    """
    return await crud.get_all(session)
