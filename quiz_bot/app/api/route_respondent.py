from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.respondent import RespondentCreate, RespondentOut
from app.db import get_db 
from app.services import service_respondent as service

router = APIRouter(prefix='/respondents', tags=['Respondents'])

@router.post('/', response_model=RespondentOut)
async def create(data: RespondentCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает нового респондента через API.

    Args:
        data (RespondentCreate): Данные для создания респондента.
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        RespondentOut: Созданный респондент или вызывает исключение при ошибке.
    """
    try:
        return await service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии респондента на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=RespondentOut)
async def get(respondent_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает респондента по его идентификатору через API.

    Args:
        respondent_id (int): Идентификатор респондента.
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        RespondentOut: Объект респондента или вызывает исключение при ошибке.
    """
    try:
        return await service.get(db, respondent_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении респондента на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/all', response_model=list[RespondentOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    """
    Получает всех респондентов через API.

    Args:
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        list[RespondentOut]: Список респондентов или вызывает исключение при ошибке.
    """
    try:
        return await service.get_all(db)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении респондентов на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
