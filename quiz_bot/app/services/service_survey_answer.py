from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_survey_answer as crud
from app.db.schemas.survey_answer import SurveyAnswerCreate, SurveyAnswerUpdate
from app.db.models import SurveyAnswers 

async def create(session: AsyncSession, data: SurveyAnswerCreate)-> SurveyAnswers | object:
    """
    Создает новый ответ на вопрос в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        data (SurveyAnswerCreate): Данные для создания ответа.

    Returns:
        SurveyAnswers | object: Объект модели SQLAlchemy при успешном создании,
        либо объект с ошибкой или пустой список при сбое.
    """
    return await crud.create(session, data)

async def get(session: AsyncSession, survey_answer_id: int) ->  SurveyAnswers | object:
    """
    Получает ответ на вопрос по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        survey_answer_id (int): Уникальный идентификатор ответа.

    Returns:
        SurveyAnswers | object: Объект модели SQLAlchemy, если найден; иначе None или объект с ошибкой.
    """
    return await crud.get(session, survey_answer_id)

async def get_all(session: AsyncSession) -> list[SurveyAnswers] | object:
    """
    Получает список всех ответов на вопросы.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.

    Returns:
        list[SurveyAnswers] | object: Список объектов ответов или пустой список при ошибке.
    """
    return await crud.get_all(session)

async def update(session: AsyncSession, survey_answer_id: int, data: SurveyAnswerUpdate)-> SurveyAnswers | object:
    
    return await crud.update(session, survey_answer_id, data)