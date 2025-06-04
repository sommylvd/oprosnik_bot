from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.enterprise import EnterpriseCreate, EnterpriseOut
from app.db import get_db 
from app.services import service_enterprise as service

router = APIRouter(prefix='/enterprises', tags=['Enterprises'])

@router.post('/', response_model=EnterpriseOut)
async def create(data: EnterpriseCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает новое предприятие через API.

    Args:
        data (EnterpriseCreate): Данные для создания предприятия.
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        EnterpriseOut: Созданное предприятие или вызывает исключение при ошибке.
    """
    try:
        return await service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии предприятия на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=EnterpriseOut)
async def get(enterprise_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает предприятие по его идентификатору через API.

    Args:
        enterprise_id (int): Идентификатор предприятия.
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        EnterpriseOut: Объект предприятия или вызывает исключение при ошибке.
    """
    try:
        return await service.get(db, enterprise_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении предприятия на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/all', response_model=list[EnterpriseOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    """
    Получает все предприятия через API.

    Args:
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        list[EnterpriseOut]: Список предприятий или вызывает исключение при ошибке.
    """
    try:
        return await service.get_all(db)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении предприятия на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
