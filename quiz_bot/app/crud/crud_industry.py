from datetime import datetime
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import (DataError, ProgrammingError, SQLAlchemyError, IntegrityError)

from app.db.models import Industries
from app.db.schemas.industry import IndustryOut, IndustryCreate

async def create(session: AsyncSession, data: IndustryCreate) -> IndustryOut | object:
    """
    Создает новую запись о промышленности в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (IndustryCreate): Данные для создания промышленности.

    Returns:
        IndustryOut | list: Объект созданной промышленности или пустой список при ошибке.
    """
    try:
        industry_data = data.model_dump()
        industry = Industries(**industry_data)
        session.add(industry)
        await session.commit()
        await session.refresh(industry)
        return industry.to_pydantic()
    except IntegrityError as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Такое имя уже существует",
            "data": industry_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
    except (ValueError, DataError, ProgrammingError, SQLAlchemyError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания промышленности",
            "data": industry_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
    
async def get(session: AsyncSession, id: int) -> IndustryOut | object:
    """
    Получает данные о промышленности по её идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        id (int): Идентификатор промышленности.

    Returns:
        IndustryOut | None: Объект промышленности или None при отсутствии/ошибке.
    """
    if id < 1:
        return None
    try:
        result = await session.execute(select(Industries).where(Industries.id == id))
        industry = result.scalar_one_or_none()
        return industry.to_pydantic() if industry else None
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения промышленности",
            "industry_id": id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all(session: AsyncSession) -> list[IndustryOut] | object:
    """
    Получает список всех промышленностей из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.

    Returns:
        list[IndustryOut] | list: Список промышленностей или пустой список при ошибке.
    """
    try:
        result = await session.execute(select(Industries))
        industrys = result.scalars().all()
        return [industry.to_pydantic() for industry in industrys]
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка промышленности",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []