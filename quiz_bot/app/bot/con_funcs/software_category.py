import logging
import httpx
from app.core.request_conf import URL, SOFTWARE_CATEGORIES, ALL

async def create_software_category(data: dict):
    """
    Создает новую категорию.

    Args:
        data (Dict[str, Any]): Словарь с данными для создания категории ПО.

    Returns:
        Dict[str, Any]: Объект созданной категории ПО при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{URL}{SOFTWARE_CATEGORIES}', json=data)
            if response.status_code != 200:
                logging.error(f"Ошибка при создании категории ПО. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                software_category = response.json()
                return software_category
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при создании категории ПО: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при создании категории ПО",
            request=e.request,
            response=e.response
        )

async def get_software_category(soft_cat_id: int):
    """
    Получает данные категории ПО по ее идентификатору.

    Args:
        software_category_id (int): Идентификатор категории ПО.

    Returns:
        Dict[str, Any]: Словарь с данными категории ПО при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{SOFTWARE_CATEGORIES}', params={'software_category_id': soft_cat_id})
            if response.status_code != 200:
                logging.error(f"Ошибка при получении категории ПО. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                software_category = response.json()
                return software_category
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении категории ПО: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении категории ПО",
            request=e.request,
            response=e.response
        )
    
async def get_software_categories():
    """
    Получает список всех категорий.

    Returns:
        List[Dict[str, Any]]: Список словарей с данными всех категорий ПО при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{SOFTWARE_CATEGORIES}{ALL}')
            if response.status_code != 200:
                logging.error(f"Ошибка при получении категорий ПО. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                software_categories = response.json()
                return software_categories
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении категорий ПО: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении категорий ПО",
            request=e.request,
            response=e.response
        )