from datetime import datetime
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import (DataError, ProgrammingError, SQLAlchemyError, IntegrityError)

from app.db.models import Questions
from app.db.schemas.question import QuestionOut, QuestionCreate

async def create(session: AsyncSession, data: QuestionCreate) -> QuestionOut | object:
    """
    Создает новый вопрос в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (QuestionCreate): Данные для создания вопроса.

    Returns:
        QuestionOut | list: Объект вопроса или пустой список при ошибке.
    """
    try:
        question_data = data.model_dump()
        question = Questions(**question_data)
        session.add(question)
        await session.commit()
        await session.refresh(question)
        return question.to_pydantic()
    except IntegrityError as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Такой номер уже существует",
            "data": question_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
    except (ValueError, DataError, ProgrammingError, SQLAlchemyError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания вопроса",
            "data": question_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
    
async def get(session: AsyncSession, id: int) -> QuestionOut | object:
    """
    Получает вопрос по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        id (int): Идентификатор вопроса.

    Returns:
        QuestionOut | None: Объект вопроса или None при отсутствии/ошибке.
    """
    if id < 1:
        return None
    try:
        result = await session.execute(select(Questions).where(Questions.id == id))
        question = result.scalar_one_or_none()
        return question.to_pydantic() if question else None
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения вопроса",
            "question_id": id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all(session: AsyncSession) -> list[QuestionOut] | object:
    """
    Получает все вопросы из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.

    Returns:
        list[QuestionOut] | list: Список вопросов или пустой список при ошибке.
    """
    try:
        result = await session.execute(select(Questions))
        questions = result.scalars().all()
        return [question.to_pydantic() for question in questions]
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка вопросов",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []