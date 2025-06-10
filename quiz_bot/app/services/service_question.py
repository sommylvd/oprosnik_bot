from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_question as crud
from app.db.schemas.question import QuestionCreate
from app.db.models import Questions 

async def create(session: AsyncSession, data: QuestionCreate)-> Questions | object:
    """
    Создает новый вопрос в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.
        data (QuestionCreate): Данные для создания нового вопроса.

    Returns:
        Questions | object: Объект вопроса при успешном создании или объект ошибки при неудаче.
    """
    return await crud.create(session, data)

async def get(session: AsyncSession, question_id: int) ->  Questions | object:
    """
    Получает вопрос по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.
        question_id (int): Уникальный идентификатор вопроса.

    Returns:
        Questions | object: Объект вопроса, если найден, или объект ошибки при неудаче.
    """
    return await crud.get(session, question_id)

async def get_all(session: AsyncSession) -> list[Questions] | object:
    """
    Получает список всех вопросов из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

    Returns:
        list[Questions] | object: Список объектов вопросов или объект ошибки при неудаче.
    """
    return await crud.get_all(session)

async def update(session: AsyncSession, question_id: int, data: QuestionCreate)-> Questions | object:

    return await crud.update(session, question_id, data)