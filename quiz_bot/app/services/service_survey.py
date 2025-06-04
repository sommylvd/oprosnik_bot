from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_survey as crud
from app.db.schemas.survey import SurveyCreate
from app.db.models import Surveys 

async def create(session: AsyncSession, data: SurveyCreate)-> Surveys | object:
    """
    Создает новый опрос в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (SurveyCreate): Данные для создания опроса.

    Returns:
        Surveys | list: Объект опроса или пустой список при ошибке.
    """
    return await crud.create(session, data)

async def get(session: AsyncSession, survey_id: int) ->  Surveys | object:
    """
    Получает опрос по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        survey_id (int): Идентификатор опроса.

    Returns:
        Surveys | None: Объект опроса или None при отсутствии/ошибке.
    """
    return await crud.get(session, survey_id)

async def get_all(session: AsyncSession) -> list[Surveys] | object:
    """
    Получает все опросы из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.

    Returns:
        list[Surveys] | list: Список опросов или пустой список при ошибке.
    """
    return await crud.get_all(session)
