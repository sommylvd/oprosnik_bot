from datetime import datetime
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.software_category import SoftwareCategoryCreate, SoftwareCategoryOut
from app.db import get_db 
from app.services import service_software_category as service

router = APIRouter(prefix='/software_categories', tags=['SoftwareCategories'])

@router.post('/', response_model=SoftwareCategoryOut)
async def create(data: SoftwareCategoryCreate, db: AsyncSession = Depends(get_db)):
    """
    Создаёт новую категорию программного обеспечения.

    Args:
        data (SoftwareCategoryCreate): Данные для создания категории.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        SoftwareCategoryOut: Данные созданной категории ПО.
    """
    try:
        return await service.create(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при созданиии категории ПО на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/', response_model=SoftwareCategoryOut)
async def get(software_category_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получает категорию программного обеспечения по ID.

    Args:
        software_category_id (int): Идентификатор категории ПО.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        SoftwareCategoryOut: Данные категории ПО.
    """
    try:
        return await service.get(db, software_category_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении категории ПО на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))

@router.get('/all', response_model=list[SoftwareCategoryOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    """
    Получает список всех категорий программного обеспечения.

    Args:
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        list[SoftwareCategoryOut]: Список всех категорий ПО.
    """
    try:
        return await service.get_all(db)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "message": "Ошибка при получении категорий ПО на стороне API",
            "error": str(e),
            "time": datetime.now().isoformat(),
        }))