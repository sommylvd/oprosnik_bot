from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.survey_answer import SurveyAnswerCreate, SurveyAnswerOut
from app.db import get_db 
from app.services import service_survey_answer as service

router = APIRouter(prefix='/survey_answers', tags=['SurveyAnswers'])

@router.post('/', response_model=SurveyAnswerOut)
async def create(data: SurveyAnswerCreate, db: AsyncSession = Depends(get_db)):

    try:
        return await service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии ответа на вопрос на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=SurveyAnswerOut)
async def get(survey_answer_id: int, db: AsyncSession = Depends(get_db)):

    try:
        return await service.get(db, survey_answer_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении ответа на вопрос на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/all', response_model=list[SurveyAnswerOut])
async def get_all(db: AsyncSession = Depends(get_db)):

    try:
        return await service.get_all(db)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении ответов на вопросы на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
