from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.industry import IndustryCreate, IndustryOut
from app.db import get_db 
from app.services import service_industry as service

router = APIRouter(prefix='/industries', tags=['Industries'])

@router.post('/', response_model=IndustryOut)
async def create(data: IndustryCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает новую промышленность через API.

    Args:
        data (IndustryCreate): Данные для создания промышленности.
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        IndustryOut: Созданная промышленность или вызывает исключение при ошибке.
    """
    try:
        return await service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии промышленности на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=IndustryOut)
async def get(industry_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает промышленность по её идентификатору через API.

    Args:
        industry_id (int): Идентификатор промышленности.
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        IndustryOut: Объект промышленности или вызывает исключение при ошибке.
    """
    try:
        return await service.get(db, industry_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении промышленности на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/all', response_model=list[IndustryOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    """
    Получает все промышленности через API.

    Args:
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        list[IndustryOut]: Список промышленностей или вызывает исключение при ошибке.
    """
    try:
        return await service.get_all(db)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении промышленностей на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
