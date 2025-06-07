import logging
import httpx
from app.core.request_conf import URL, QUESTIONS, ALL

async def create_question(data: dict):
    """
    Создает новый вопрос или возвращает существующий по уникальному номеру.

    Args:
        data (dict): Словарь с данными для создания вопроса (например, {"text": "Вопрос", "number": 1, "answer_type": "string"}).

    Returns:
        dict: Объект созданного или существующего вопроса при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        # Убедимся, что number и answer_type присутствуют
        data.setdefault("answer_type", "string")
        if "number" not in data:
            data["number"] = 1  # Значение по умолчанию, если не указано

        async with httpx.AsyncClient() as client:
            # Сначала проверяем, существует ли вопрос с таким number
            response = await client.get(f'{URL}{QUESTIONS}', params={'number': data["number"]})
            if response.status_code == 200:
                questions = response.json()
                if questions and len(questions) > 0:
                    logging.info(f"Вопрос с number {data['number']} уже существует, возвращаем существующий.")
                    return questions[0]  # Возвращаем первый совпавший вопрос

            # Если вопроса нет, создаем новый
            response = await client.post(f'{URL}{QUESTIONS}', json=data)
            if response.status_code != 200:
                logging.error(f"Ошибка при создании вопроса. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                question = response.json()
                return question
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при создании вопроса: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при создании вопроса",
            request=e.request,
            response=e.response
        )

async def get_question(question_id: int):
    """
    Получает данные вопроса по его идентификатору.

    Args:
        question_id (int): Идентификатор вопроса.

    Returns:
        dict: Данные вопроса при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{QUESTIONS}', params={'question_id': question_id})
            if response.status_code != 200:
                logging.error(f"Ошибка при получении вопроса. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                question = response.json()
                return question
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении вопроса: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении вопроса",
            request=e.request,
            response=e.response
        )
    
async def get_questions():
    """
    Получает список всех вопросов.

    Returns:
        list: Список словарей с данными всех вопросов при успешном запросе.

    Raises:
        httpx.HTTPStatusError: Если сервер вернул ошибку HTTP.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{QUESTIONS}{ALL}')
            if response.status_code != 200:
                logging.error(f"Ошибка при получении вопросов. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                questions = response.json()
                return questions
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении вопросов: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении вопросов",
            request=e.request,
            response=e.response
        )