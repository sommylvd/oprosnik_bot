
from datetime import datetime
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import (DataError, ProgrammingError, SQLAlchemyError, IntegrityError)

from app.db.models import Enterprises
from app.db.schemas.enterprise import EnterpriseOut, EnterpriseCreate

async def create(session: AsyncSession, data: EnterpriseCreate) -> EnterpriseOut | object:
    """
    Создает новое предприятие в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        data (EnterpriseCreate): Данные для создания предприятия.

    Returns:
        EnterpriseOut | list: Объект созданного предприятия или пустой список при ошибке.

    Работа:
        - Конвертирует Pydantic-объект в словарь
        - Создает ORM-объект Enterprises
        - Сохраняет в БД и обновляет объект
        - Возвращает EnterpriseOut-представление
    """
    try:
        enterprise_data = data.model_dump()
        
        enterprise = Enterprises(**enterprise_data)
        session.add(enterprise)
        await session.commit()
        await session.refresh(enterprise)
        return enterprise.to_pydantic()
    
    except IntegrityError as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Такой ",
            "data": enterprise_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
    except (ValueError, DataError, ProgrammingError, SQLAlchemyError) as e:
        await session.rollback()
        logging.error(json.dumps({
            "message": "Ошибка создания предприятия",
            "data": enterprise_data,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []
    
async def get(session: AsyncSession, id: int) -> EnterpriseOut | object:
    """
    Получает предприятие по ID из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        id (int): Идентификатор предприятия.

    Returns:
        EnterpriseOut | list: Объект предприятия или пустой список при ошибке/отсутствии.

    Работа:
        - Проверяет валидность ID
        - Выполняет асинхронный запрос к БД
        - Конвертирует результат в Pydantic-объект
    """
    if id < 1:
        return None
    try:
        result = await session.execute(select(Enterprises).where(Enterprises.id == id))
        enterprise = result.scalar_one_or_none()
        return enterprise.to_pydantic() if enterprise else None
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения предприятия",
            "enterprise_id": id,
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return None

async def get_all(session: AsyncSession) -> list[EnterpriseOut] | object:
    """
    Получает все предприятия из базы данных.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.

    Returns:
        list[EnterpriseOut] | list: Список предприятий или пустой список при ошибке.

    Работа:
        - Выполняет асинхронный запрос всех предприятий
        - Конвертирует результаты в список Pydantic-объектов
    """
    try:
        result = await session.execute(select(Enterprises))
        enterprises = result.scalars().all()
        return [enterprise.to_pydantic() for enterprise in enterprises]
    except SQLAlchemyError as e:
        logging.error(json.dumps({
            "message": "Ошибка получения списка предприятий",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
        return []