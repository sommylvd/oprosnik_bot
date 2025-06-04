from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_respondent as crud
from app.db.schemas.respondent import RespondentCreate
from app.db.models import Respondents 

async def create(session: AsyncSession, data: RespondentCreate)-> Respondents | object:
    """
    Создает нового респондента в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (RespondentCreate): Данные для создания респондента.

    Returns:
        Respondents | list: Объект респондента или пустой список при ошибке.
    """
    return await crud.create(session, data)

async def get(session: AsyncSession, respondent_id: int) ->  Respondents | object:
    """
    Получает респондента по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        respondent_id (int): Идентификатор респондента.

    Returns:
        Respondents | None: Объект респондента или None при отсутствии/ошибке.
    """
    return await crud.get(session, respondent_id)

async def get_all(session: AsyncSession) -> list[Respondents] | object:
    """
    Получает всех респондентов из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.

    Returns:
        list[Respondents] | list: Список респондентов или пустой список при ошибке.
    """
    return await crud.get_all(session)
