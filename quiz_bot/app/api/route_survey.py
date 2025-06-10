from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.survey import SurveyCreate, SurveyOut, SurveyUpdate
from app.db import get_db 
from app.services import service_survey as service

router = APIRouter(prefix='/surveys', tags=['Surveys'])

@router.post('/', response_model=SurveyOut)
async def create(data: SurveyCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает новый опрос через API.

    Args:
        data (SurveyCreate): Данные для создания опроса.
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        SurveyOut: Созданный опрос или вызывает исключение при ошибке.
    """
    try:
        return await service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии опроса на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=SurveyOut)
async def get(survey_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает опрос по его идентификатору через API.

    Args:
        survey_id (int): Идентификатор опроса.
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        SurveyOut: Объект опроса или вызывает исключение при ошибке.
    """
    try:
        return await service.get(db, survey_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении опроса на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/all', response_model=list[SurveyOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    """
    Получает все опросы через API.

    Args:
        db (AsyncSession): Асинхронная сессия БД (автоматически внедряется).

    Returns:
        list[SurveyOut]: Список опросов или вызывает исключение при ошибке.
    """
    try:
        return await service.get_all(db)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении опросов на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.put('/', response_model=SurveyOut)
async def update(survey_id: int, data: SurveyUpdate, db: AsyncSession = Depends(get_db)):
    try:
        return await service.update(db, survey_id, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при обновлении опроса на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))