import asyncio
import json
from pprint import pprint

import aiofiles
import aiohttp
from loguru import logger

from config import headers_ozon


async def get_limit():
    """Лимиты на ассортимент, создание и обновление товаров"""
    url = 'https://api-seller.ozon.ru/v4/product/info/limit'
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.post(url, headers=headers_ozon, json={'language': 'RU'}) as response:
            print("Status:", response.status)
            data = await response.json()
            async with aiofiles.open(f'../files_ozon/limit.json', 'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data, ensure_ascii=False, indent=4)}')


async def fetch_cards(session, url, data_json):
    """Асинхронный запрос к API для получения карточек товаров"""
    try:
        async with session.post(url, headers=headers_ozon, json=data_json) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Ошибка {response.status}: {await response.text()}")
                return None
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return None


async def get_cards(limit=1000, archived=False):
    """Получение списка товаров"""
    url = 'https://api-seller.ozon.ru/v2/product/list'
    result = []

    async def get_list_arts(visibility="ALL"):
        file_path = f'../files_ozon/atr_list_{visibility}.json'
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            data_json = {
                "filter": {
                    "visibility": visibility
                },
                "last_id": "",
                "limit": limit
            }
            while True:
                data = await fetch_cards(session, url, data_json)
                if not data:
                    break
                cards = data.get("result", {}).get('items')
                result.extend(cards)
                last_id = data['result']['last_id']
                current_count = len(result)
                logger.info(f"Получено {current_count}")
                if len(cards) < limit:
                    break

                # Обновляем курсор для следующего запроса
                data_json["last_id"] = last_id
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data, ensure_ascii=False, indent=4)}')

    await get_list_arts()
    if archived:
        await get_list_arts("ARCHIVED")


async def get_prod_info(offer_id: str, product_id: int):
    """Получение информации о товаре"""
    url = 'https://api-seller.ozon.ru/v2/product/info'
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        json_push = {
            "offer_id": offer_id,
            "product_id": product_id,
            "sku": 0
        }
        async with session.post(url, headers=headers_ozon, json=json_push) as response:
            print("Status:", response.status)
            data = await response.json()
            async with aiofiles.open(f'../files_ozon/{offer_id}.json', 'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data, ensure_ascii=False, indent=4)}')


if __name__ == '__main__':
    asyncio.run(get_cards(archived=True))

    # offer_id = 'NAKLEIKIKVADRAT-OPM_GARU-UV-16'
    # product_id = 1146963401
    # asyncio.run(get_prod_info(offer_id, product_id))

