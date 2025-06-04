from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_software_category as crud
from app.db.schemas.software_category import SoftwareCategoryCreate
from app.db.models import SoftwareCategories

async def create(session: AsyncSession, data: SoftwareCategoryCreate)-> SoftwareCategories | object:
    """
    Создаёт новую категорию программного обеспечения.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        data (SoftwareCategoryCreate): Данные для создания новой категории ПО.

    Returns:
        SoftwareCategories: Созданный объект модели категории ПО.
        object: Альтернативный тип для совместимости с обработкой ошибок.
    """
    return await crud.create(session, data)

async def get(session: AsyncSession, software_category_id: int) ->  SoftwareCategories | object:
    """
    Возвращает категорию программного обеспечения по ID.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        software_category_id (int): Идентификатор категории ПО.

    Returns:
        SoftwareCategories: Объект модели, если найден.
        None | object: None или альтернативный объект, если не найдено или возникла ошибка.
    """
    return await crud.get(session, software_category_id)

async def get_all(session: AsyncSession) -> list[SoftwareCategories] | object:
    """
    Возвращает список всех категорий программного обеспечения.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        list[SoftwareCategories]: Список всех объектов категорий.
        object: Альтернативный тип при ошибке.
    """
    return await crud.get_all(session)
