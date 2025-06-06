import logging
import httpx
from app.core.request_conf import URL, SURVEY_ANSWERS, ALL

async def create_survey_answer(data: dict):
    """
    Создает новый ответ на опрос.

    Args:
        data (Dict[str, Any]): Словарь с данными для создания ответа на опрос.

    Returns:
        Dict[str, Any]: Объект созданного ответа при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{URL}{SURVEY_ANSWERS}', json=data)
            response.raise_for_status()
            if response.status_code == 200:
                survey_answer = response.json()
                return survey_answer
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при создании ответа на опрос: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при создании ответа на опрос")

async def get_survey_answer(sur_ans_id: int):
    """
    Получает данные ответа на опрос по его идентификатору.

    Args:
        survey_answer_id (int): Идентификатор ответа на опрос.

    Returns:
        Dict[str, Any]: Словарь с данными ответа при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{SURVEY_ANSWERS}', params={'survey_answer_id': sur_ans_id})
            response.raise_for_status()
            if response.status_code == 200:
                survey_answer = response.json()
                return survey_answer
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении ответа на опрос: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении ответа на опрос")
    
async def get_survey_answers():
    """
    Получает список всех ответов на опросы.

    Returns:
        List[Dict[str, Any]]: Список словарей с данными всех ответов при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{SURVEY_ANSWERS}{ALL}')
            response.raise_for_status()
            if response.status_code == 200:
                survey_answers = response.json()
                return survey_answers
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении ответов на опросы: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении ответов на опросы")