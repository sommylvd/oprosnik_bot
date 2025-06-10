from datetime import datetime
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import (DataError, ProgrammingError, SQLAlchemyError, IntegrityError)

from app.db.models import SurveyAnswers
from app.db.schemas.survey_answer import SurveyAnswerOut, SurveyAnswerCreate, SurveyAnswerUpdate

async def create(session: AsyncSession, data: SurveyAnswerCreate) -> SurveyAnswerOut | object:
    """
    Создает новый ответ на вопрос в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        data (SurveyAnswerCreate): Данные для создания ответа на вопрос.

    Returns:
        SurveyAnswerOut | object: Объект ответа в формате Pydantic при успешном создании,
        либо пустой список при ошибке.
    """
    try:
        sur_ans_data = data.model_dump()
        sur_ans = SurveyAnswers(**sur_ans_data)
        session.add(sur_ans)
        await session.commit()
        await session.refresh(sur_ans)
        return sur_ans.to_pydantic()
    except Exception as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания ответа на вопрос",
            "data": sur_ans_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
    
async def get(session: AsyncSession, id: int, as_pydantic: bool = True) -> SurveyAnswerOut | object:
    """
    Получает ответ на вопрос по ID из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        id (int): Идентификатор ответа.

    Returns:
        SurveyAnswerOut | object: Объект ответа в формате Pydantic, если найден;
        None при отсутствии записи или ошибке запроса.
    """
    if id < 1:
        return None
    try:
        result = await session.execute(select(SurveyAnswers).where(SurveyAnswers.id == id))
        sur_ans = result.scalar_one_or_none()
        if as_pydantic is False:
            return sur_ans if sur_ans else None
        return sur_ans.to_pydantic() if sur_ans else None
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка получения ответа на вопрос",
            "sur_ans_id": id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all(session: AsyncSession) -> list[SurveyAnswerOut] | object:
    """
    Получает список всех ответов на вопросы из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.

    Returns:
        list[SurveyAnswerOut] | object: Список объектов ответов в формате Pydantic;
        пустой список при ошибке запроса.
    """
    try:
        result = await session.execute(select(SurveyAnswers))
        sur_anss = result.scalars().all()
        return [sur_ans.to_pydantic() for sur_ans in sur_anss]
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка ответов на вопросы",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []

async def update(session: AsyncSession, id: int, data: SurveyAnswerUpdate) -> SurveyAnswerOut | object:
    if id < 1:
        return None
    try:

        sur_ans = await get(session, id, False)
        if not sur_ans:
            return None
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(sur_ans, key, value)
        
        await session.commit()
        await session.refresh(sur_ans)
        return sur_ans.to_pydantic()
    
    except Exception as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка обновлении ответа на вопрос",
            "data": sur_ans.model_dump(),
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []