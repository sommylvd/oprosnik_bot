from datetime import datetime
import json
import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import (DataError, ProgrammingError, SQLAlchemyError, IntegrityError)

from app.db.models import Surveys
from app.db.schemas.survey import SurveyOut, SurveyCreate

async def parse_naive_datetime(date_input: str | datetime) -> datetime:
    """
    Преобразует строку или datetime в naive datetime (без таймзоны).
    Бросает HTTPException при ошибке парсинга или наличии tzinfo.
    """
    if isinstance(date_input, str):
        try:
            date_input = datetime.fromisoformat(date_input)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Неверный формат даты. Используй ISO 8601, например: '2025-04-23T14:30:00'"
            )
    if date_input.tzinfo is not None:
        date_input = date_input.replace(tzinfo=None)
    return date_input

async def create(session: AsyncSession, data: SurveyCreate) -> SurveyOut | object:
    """
    Создает новый опрос в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (SurveyCreate): Данные для создания опроса.

    Returns:
        SurveyOut | list: Объект опроса или пустой список при ошибке.
    """
    try:
        started_at = await parse_naive_datetime(data.started_at)
        completed_at = data.completed_at
        if data.completed_at:
            completed_at = await parse_naive_datetime(data.completed_at)
        
        survey = Surveys(
            respondent_id=data.respondent_id,
            started_at=started_at,
            completed_at=completed_at,
            user_agent=data.user_agent
        )
        session.add(survey)
        await session.commit()
        await session.refresh(survey)
        return survey.to_pydantic()
    except (ValueError, DataError, ProgrammingError, SQLAlchemyError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания опроса",
            "data": survey.to_pydantic(),
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
    
async def get(session: AsyncSession, id: int) -> SurveyOut | object:
    """
    Получает опрос по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        id (int): Идентификатор опроса.

    Returns:
        SurveyOut | None: Объект опроса или None при отсутствии/ошибке.
    """
    if id < 1:
        return None
    try:
        result = await session.execute(select(Surveys).where(Surveys.id == id))
        survey = result.scalar_one_or_none()
        return survey.to_pydantic() if survey else None
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения опроса",
            "survey_id": id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all(session: AsyncSession) -> list[SurveyOut] | object:
    """
    Получает все опросы из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.

    Returns:
        list[SurveyOut] | list: Список опросов или пустой список при ошибке.
    """
    try:
        result = await session.execute(select(Surveys))
        surveys = result.scalars().all()
        return [survey.to_pydantic() for survey in surveys]
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка опросов",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []