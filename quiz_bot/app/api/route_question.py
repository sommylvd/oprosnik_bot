from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.question import QuestionCreate, QuestionOut
from app.db import get_db 
from app.services import service_question as service

router = APIRouter(prefix='/questions', tags=['Questions'])

@router.post('/', response_model=QuestionOut)
async def create(data: QuestionCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает новый вопрос.

    Args:
        data (QuestionCreate): Данные для создания вопроса.
        db (AsyncSession): Асинхронная сессия с базой данных.

    Returns:
        QuestionOut: Созданный вопрос.
    """
    try:
        return await service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии вопроса на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=QuestionOut)
async def get(question_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает вопрос по ID отрасли.

    Args:
        industry_id (int): Идентификатор вопроса (или отрасли, если это привязано).
        db (AsyncSession): Асинхронная сессия с базой данных.

    Returns:
        QuestionOut: Найденный вопрос.
    """
    try:
        return await service.get(db, question_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении вопроса на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/all', response_model=list[QuestionOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    """
    Получает список всех вопросов.

    Args:
        db (AsyncSession): Асинхронная сессия с базой данных.

    Returns:
        list[QuestionOut]: Список всех вопросов.
    """
    try:
        return await service.get_all(db)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении вопросов на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
