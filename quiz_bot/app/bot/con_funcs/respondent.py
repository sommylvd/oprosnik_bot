import logging
import httpx
from app.core.request_conf import URL, RESPONDENTS, ALL

async def create_respondent(data: dict):
    """
    Создает нового респондента.

    Args:
        data (Dict[str, Any]): Словарь с данными для создания респондента.

    Returns:
        Dict[str, Any]: Объект созданного респондента при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{URL}{RESPONDENTS}', json=data)
            response.raise_for_status()
            if response.status_code == 200:
                respondent = response.json()
                return respondent
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при создании респондента: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при создании респондента")

async def get_respondent(respondent_id: int):
    """
    Получает данные респондента по его идентификатору.

    Args:
        respondent_id (int): Идентификатор респондента.

    Returns:
        Dict[str, Any]: Словарь с данными респондента при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{RESPONDENTS}', params={'respondent_id': respondent_id})
            response.raise_for_status()
            if response.status_code == 200:
                respondent = response.json()
                return respondent
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении респондента: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении респондента")
    
async def get_respondents():
    """
    Получает список всех респондентов.

    Returns:
        List[Dict[str, Any]]: Список словарей с данными всех респондентов при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{RESPONDENTS}{ALL}')
            response.raise_for_status()
            if response.status_code == 200:
                respondents = response.json()
                return respondents
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении респондентов: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении респондентов")