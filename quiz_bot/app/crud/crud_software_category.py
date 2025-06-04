from datetime import datetime
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import (DataError, ProgrammingError, SQLAlchemyError, IntegrityError)

from app.db.models import SoftwareCategories
from app.db.schemas.software_category import SoftwareCategoryOut, SoftwareCategoryCreate

async def create(session: AsyncSession, data: SoftwareCategoryCreate) -> SoftwareCategoryOut | object:
    """
    Создаёт новую категорию программного обеспечения.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        data (SoftwareCategoryCreate): Данные для создания категории.

    Returns:
        SoftwareCategoryOut: Созданная категория в формате схемы.
        object: Пустой список, если произошла ошибка (для совместимости с FastAPI).
    """
    try:
        soft_cat_data = data.model_dump()
        soft_cat = SoftwareCategories(**soft_cat_data)
        session.add(soft_cat)
        await session.commit()
        await session.refresh(soft_cat)
        return soft_cat.to_pydantic()
    except IntegrityError as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Такое имя уже существует",
            "data": soft_cat_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
    except (ValueError, DataError, ProgrammingError, SQLAlchemyError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания категории ПО",
            "data": soft_cat_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
    
async def get(session: AsyncSession, id: int) -> SoftwareCategoryOut | object:
    """
    Получает категорию программного обеспечения по её ID.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        id (int): ID категории.

    Returns:
        SoftwareCategoryOut: Найденная категория в формате схемы.
        None: Если категория не найдена или ID некорректен.
    """
    if id < 1:
        return None
    try:
        result = await session.execute(select(SoftwareCategories).where(SoftwareCategories.id == id))
        soft_cat = result.scalar_one_or_none()
        return soft_cat.to_pydantic() if soft_cat else None
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения категории ПО",
            "soft_cat_id": id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all(session: AsyncSession) -> list[SoftwareCategoryOut] | object:
    """
    Возвращает список всех категорий программного обеспечения.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        list[SoftwareCategoryOut]: Список всех категорий.
        object: Пустой список, если произошла ошибка.
    """
    try:
        result = await session.execute(select(SoftwareCategories))
        soft_cats = result.scalars().all()
        return [soft_cat.to_pydantic() for soft_cat in soft_cats]
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка категорий ПО",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []