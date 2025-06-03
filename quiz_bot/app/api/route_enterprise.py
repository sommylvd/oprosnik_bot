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
    try:
        return await service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии категории на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=EnterpriseOut)
async def get(enterprise_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await service.get(db, enterprise_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении категорий на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/all', response_model=list[EnterpriseOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    try:
        return await service.get_all(db)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении категорий на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))
