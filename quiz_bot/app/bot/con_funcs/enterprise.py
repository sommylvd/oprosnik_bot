import logging
import httpx
from app.core.request_conf import URL, ENTERPRISES, ALL

async def create_enterprise(data: dict):
    """
    Создает новое предприятие.

    Args:
        data (dict): Данные предприятия для отправки в API.

    Returns:
        dict: Объект созданного предприятия при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{URL}{ENTERPRISES}', json=data)
            if response.status_code != 200:
                logging.error(f"Ошибка при создании предприятия. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                enterprise = response.json()
                return enterprise
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при создании предприятия: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при создании предприятия",
            request=e.request,
            response=e.response
        )

async def get_enterprise(enterprise_id: int):
    """
    Получает предприятие по ID.

    Args:
        enterprise_id (int): Идентификатор предприятия.

    Returns:
        dict: Данные предприятия при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{ENTERPRISES}', params={'enterprise_id': enterprise_id})
            if response.status_code != 200:
                logging.error(f"Ошибка при получении предприятия. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                enterprise = response.json()
                return enterprise
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении предприятия: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении предприятия",
            request=e.request,
            response=e.response
        )
    
async def get_enterprises():
    """
    Получает список всех предприятий.

    Returns:
        list: Список предприятий при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{ENTERPRISES}{ALL}')
            if response.status_code != 200:
                logging.error(f"Ошибка при получении предприятий. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                enterprises = response.json()
                return enterprises
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении предприятий: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении предприятий",
            request=e.request,
            response=e.response
        )
    
async def update_enterprise(enterprise_id: int, data: dict):
    """
    Обновляет существующее предприятие.

    Args:
        enterprise_id (int): Идентификатор предприятия.
        data (EnterpriseUpdate): Данные для обновления предприятия.

    Returns:
        dict: Объект обновлённого предприятия при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f'{URL}{ENTERPRISES}', params={'enterprise_id': enterprise_id}, json=data)
            if response.status_code != 200:
                logging.error(f"Ошибка при обновлении предприятия. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                enterprise = response.json()
                return enterprise
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при обновлении предприятия: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при обновлении предприятия",
            request=e.request,
            response=e.response
        )