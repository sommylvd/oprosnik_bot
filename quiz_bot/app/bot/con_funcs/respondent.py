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
            if response.status_code != 200:
                logging.error(f"Ошибка при создании респондента. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                respondent = response.json()
                return respondent
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при создании респондента: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при создании респондента",
            request=e.request,
            response=e.response
        )

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
            if response.status_code != 200:
                logging.error(f"Ошибка при получении респондента. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                respondent = response.json()
                return respondent
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении респондента: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении респондента",
            request=e.request,
            response=e.response
        )
    
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
            if response.status_code != 200:
                logging.error(f"Ошибка при получении респондентов. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                respondents = response.json()
                return respondents
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении респондентов: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении респондентов",
            request=e.request,
            response=e.response
        )
    

async def update_respondent(respondent_id: int, respondent_data: dict, enterprise_id: int):
    """Обновить данные респондента"""
    # Проверяем обязательные параметры
    if not respondent_id:
        logging.error("Respondent ID is missing")
        return None
        
    if not enterprise_id:
        logging.error("Enterprise ID is missing")
        return None
        
    # Формируем полные данные
    full_data = {
        **respondent_data,
        "enterprise_id": enterprise_id
    }
    
    # Формируем query-параметры
    params = {"respondent_id": respondent_id}
    
    logging.info(f"Updating respondent {respondent_id} with data: {full_data}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f'{URL}{RESPONDENTS}',
                json=full_data,
                params=params
            )
            
            if response.status_code == 200:
                logging.info(f"Respondent {respondent_id} updated successfully")
                return response.json()
            
            # Логируем ошибки
            try:
                error_body = response.json()
                logging.error(f"Error updating respondent. Code: {response.status_code}, Body: {error_body}")
            except:
                logging.error(f"Error updating respondent: {response.status_code} {response.text}")
            
            return None
            
    except Exception as e:
        logging.error(f"Exception while updating respondent: {str(e)}")
        return None