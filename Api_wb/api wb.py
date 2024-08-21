import asyncio
import datetime
import glob
import json
import time
from pprint import pprint

import aiohttp
from loguru import logger

from config import get_headers_wb, BASE_DIR, dict_tokens, tokens_wb
from utils import chunks, create_json, read_json


async def get_characters(subjectId: int, token: str):
    """Получение харктеристик указанной категории"""
    url = f'https://content-api.wildberries.ru/content/v2/object/charcs/'
    params = {'subjectId': subjectId}
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params, headers=get_headers_wb(token)) as response:
            # print("Status:", response.status)
            pprint(await response.json())


async def fetch_cards(token, session, url, data_json):
    """Асинхронный запрос к API для получения карточек товаров"""
    try:
        async with session.post(url, headers=get_headers_wb(token), data=data_json) as response:
            if response.status == 200:
                return await response.json()
            elif response.status in [500, 504]:
                logger.warning(f"Ошибка {response.status}: {await response.text()}. Повторный запрос.")
                return None
            else:
                logger.error(f"Ошибка {response.status}: {await response.text()}")
                return None
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return None


async def async_parser_wb_cards(token, index) -> list[dict]:
    """Асинхронное получение карточек товаров"""
    url_all_cards = "https://content-api.wildberries.ru/content/v2/get/cards/list"

    max_attempts = 5
    time_sleep = 15
    limit = 100

    result = []  # Здесь будем хранить все полученные данные
    data = {
        "settings": {
            "sort": {
                "ascending": False
            },
            "cursor": {
                "limit": limit
            },
            "filter": {
                "withPhoto": -1
            }
        }
    }

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        while True:
            data_json = json.dumps(data)
            attempts = 0
            while attempts < max_attempts:
                response_data = await fetch_cards(token, session, url_all_cards, data_json)
                if response_data:
                    break
                attempts += 1
                if attempts < max_attempts:
                    logger.info(f"Попытка {attempts}/{max_attempts}. Ожидание {time_sleep} секунд.")
                    await asyncio.sleep(time_sleep)
                else:
                    logger.error(f"Достигнут лимит попыток ({max_attempts}). Прекращаем выполнение.")
                    return result

            if not response_data:
                break

            result.extend(response_data.get("cards", []))
            total = response_data['cursor']['total']
            nmID = response_data['cursor']['nmID']
            updatedAt = response_data['cursor'].get('updatedAt', None)
            current_count = len(result)
            logger.info(f"Получено {current_count}")

            if total < limit:
                break

            # Обновляем курсор для следующего запроса
            data["settings"]["cursor"]["updatedAt"] = updatedAt
            data["settings"]["cursor"]["nmID"] = nmID

    with open(f'{BASE_DIR}/files_wb/wildberries_data_cards_{index}.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
        logger.success(f"Все данные сохранены в файл 'wildberries_data_cards_{index}.json'")
    return result


async def update_card(token, data: list[dict]):
    """Редактирование КТ"""
    url = 'https://content-api.wildberries.ru/content/v2/cards/update'
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=data, headers=get_headers_wb(token)) as response:
            print("Status:", response.status)
            if response.status != 200:
                logger.error(await response.json())


def push_update_data_to_wb(target_index_lk: int, num: int = 1000):
    """Обнговление массива карточек на WB"""
    """params:
    target_index_lk: индекс кабинета
    num: кол-во карточек в 1 запросе;
    """
    files_data_wb = glob.glob(f'{BASE_DIR}/files_wb/result_push_data_*')
    for index, file in enumerate(files_data_wb, start=1):
        index_lk = int(file.split('_')[-1].replace('.json', ''))
        if index_lk == target_index_lk:
            data = read_json(file)
            if data:
                for chunk in chunks(data, num):
                    asyncio.run(update_card(dict_tokens[index_lk], chunk))
                    time.sleep(3)
        # else:
        #     logger.error(f'Не найден файл для личного кабинета {target_index_lk}')


if __name__ == '__main__':
    # asyncio.run(get_characters(token, url, subjectId))
    print(tokens_wb)
    for index, token in enumerate(tokens_wb, start=1):
        start = datetime.datetime.now()
        asyncio.run(async_parser_wb_cards(token, index))
        logger.debug(datetime.datetime.now() - start)
    # push_update_data_to_wb(1)
