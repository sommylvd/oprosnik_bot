from datetime import datetime
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import (DataError, ProgrammingError, SQLAlchemyError, IntegrityError)

from app.db.models import Respondents
from app.db.schemas.respondent import RespondentOut, RespondentCreate, RespondentUpdate

async def create(session: AsyncSession, data: RespondentCreate) -> RespondentOut | object:
    """
    Создает нового респондента в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (RespondentCreate): Данные для создания респондента.

    Returns:
        RespondentOut | list: Объект респондента или пустой список при ошибке.
    """
    try:
        respondent_data = data.model_dump()
        respondent = Respondents(**respondent_data)
        session.add(respondent)
        await session.commit()
        await session.refresh(respondent)
        return respondent.to_pydantic()
    except Exception as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания респондента",
            "data": respondent_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
    
async def get(session: AsyncSession, id: int, as_pydantic: bool = True) -> RespondentOut | object:
    """
    Получает респондента по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        id (int): Идентификатор респондента.

    Returns:
        RespondentOut | None: Объект респондента или None при отсутствии/ошибке.
    """
    if id < 1:
        return None
    try:
        result = await session.execute(select(Respondents).where(Respondents.id == id))
        respondent = result.scalar_one_or_none()
        if as_pydantic is False:
            return respondent if respondent else None
        return respondent.to_pydantic() if respondent else None
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка получения респондента",
            "respondent_id": id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all(session: AsyncSession) -> list[RespondentOut] | object:
    """
    Получает всех респондентов из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.

    Returns:
        list[RespondentOut] | list: Список респондентов или пустой список при ошибке.
    """
    try:
        result = await session.execute(select(Respondents))
        respondents = result.scalars().all()
        return [respondent.to_pydantic() for respondent in respondents]
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка респондентов",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
    
async def update(session: AsyncSession, id: int, data: RespondentUpdate) -> RespondentOut | object:
    if id < 1:
        return None
    try:

        respondent = await get(session, id, False)
        if not respondent:
            return None
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(respondent, key, value)
        
        await session.commit()
        await session.refresh(respondent)
        return respondent.to_pydantic()
    
    except Exception as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания респондента",
            "data": respondent.model_dump(),
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []