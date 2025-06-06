import logging
import httpx
from app.core.request_conf import URL, QUESTIONS, ALL

async def create_question(data: dict):
    """
    Создает новый вопрос.

    Args:
        data (Dict[str, Any]): Словарь с данными для создания вопроса.

    Returns:
        Dict[str, Any]: Объект созданного вопроса при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{URL}{QUESTIONS}', json=data)
            response.raise_for_status()
            if response.status_code == 200:
                question = response.json()
                return question
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при создании вопроса: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при создании вопроса")

async def get_question(question_id: int):
    """
    Получает данные вопроса по его идентификатору.

    Args:
        question_id (int): Идентификатор вопроса.

    Returns:
        Dict[str, Any]: Словарь с данными вопроса при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{QUESTIONS}', params={'question_id': question_id})
            response.raise_for_status()
            if response.status_code == 200:
                question = response.json()
                return question
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении вопроса: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении вопроса")
    
async def get_questions():
    """
    Получает список всех вопросов.

    Returns:
        List[Dict[str, Any]]: Список словарей с данными всех вопросов при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{QUESTIONS}{ALL}')
            response.raise_for_status()
            if response.status_code == 200:
                questions = response.json()
                return questions
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении вопросов: {str(e)}")
        raise httpx._exceptions.HTTPStatusError(message="Произошла ошибка при получении вопросов")