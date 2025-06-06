import logging
import httpx
from app.core.request_conf import URL, INDUSTRIES, ALL

async def create_industry(data: dict):
    """
    Создает новую отрасль.

    Args:
        data (Dict[str, Any]): Словарь с данными для создания отрасли.

    Returns:
        Dict[str, Any]: Объект созданной отрасли при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{URL}{INDUSTRIES}', json=data)
            response.raise_for_status()
            if response.status_code == 200:
                industry = response.json()
                return industry
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при создании промышлинности: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при создании промышлинности")

async def get_industry(industry_id: int):
    """
    Получает данные отрасли по ее идентификатору.

    Args:
        industry_id (int): Идентификатор отрасли.

    Returns:
        Dict[str, Any]: Словарь с данными отрасли при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{INDUSTRIES}', params={'industry_id': industry_id})
            response.raise_for_status()
            if response.status_code == 200:
                industry = response.json()
                return industry
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении промышлинности: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении промышлинности")
    
async def get_industries():
    """
    Получает список всех отраслей.

    Returns:
        List[Dict[str, Any]]: Список словарей с данными всех отраслей при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{INDUSTRIES}{ALL}')
            response.raise_for_status()
            if response.status_code == 200:
                industries = response.json()
                return industries
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении промышлинностей: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении промышлинностей")