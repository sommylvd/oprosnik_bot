import logging
import httpx
from app.core.request_conf import URL, SURVEYS, ALL

async def create_survey(data: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{URL}{SURVEYS}', json=data)
            if response.status_code != 200:
                logging.error(f"Ошибка при создании опроса. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                survey = response.json()
                return survey
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при создании опроса: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при создании опроса",
            request=e.request,
            response=e.response
        )

async def get_survey(sur_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{SURVEYS}', params={'survey_id': sur_id})
            if response.status_code != 200:
                logging.error(f"Ошибка при получении опроса. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                survey = response.json()
                return survey
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении опроса: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении опроса",
            request=e.request,
            response=e.response
        )
    
async def get_surveys():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{URL}{SURVEYS}{ALL}')
            if response.status_code != 200:
                logging.error(f"Ошибка при получении опросов. Код: {response.status_code}, Тело ответа: {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                surveys = response.json()
                return surveys
    except httpx.HTTPStatusError as e:
        logging.exception(f"Произошла ошибка при получении опросов: {str(e)}")
        raise httpx.HTTPStatusError(
            message="Произошла ошибка при получении опросов",
            request=e.request,
            response=e.response
        )