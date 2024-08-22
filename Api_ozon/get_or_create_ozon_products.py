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
            data_res = await response.json()
            async with aiofiles.open(f'../files_ozon/limit.json', 'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data_res, ensure_ascii=False, indent=4)}')


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
                data_res = await fetch_cards(session, url, data_json)
                if not data_res:
                    break
                cards = data_res.get("result", {}).get('items')
                result.extend(cards)
                last_id = data_res['result']['last_id']
                current_count = len(result)
                logger.info(f"Получено {current_count}")
                if len(cards) < limit:
                    break

                # Обновляем курсор для следующего запроса
                data_json["last_id"] = last_id
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data_res, ensure_ascii=False, indent=4)}')

    await get_list_arts()
    if archived:
        await get_list_arts("ARCHIVED")


async def get_card_info(offer_id: str, product_id: int):
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
            data_res = await response.json()
            async with aiofiles.open(f'../files_ozon/{offer_id}.json', 'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data_res, ensure_ascii=False, indent=4)}')


async def create_card(art, data):
    """Создание карточки"""
    url = 'https://api-seller.ozon.ru/v3/product/import'
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.post(url, headers=headers_ozon, json=data) as response:
            print("Status:", response.status)
            data_res = await response.json()
            async with aiofiles.open(f'../files_ozon/{art}.json', 'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data_res, ensure_ascii=False, indent=4)}')


async def info_task_id(task_id):
    """Узнать статус добавления товара"""
    url = 'https://api-seller.ozon.ru/v1/product/import/info'
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.post(url, headers=headers_ozon, json={"task_id": task_id}) as response:
            print("Status:", response.status)
            data_res = await response.json()
            async with aiofiles.open(f'../files_ozon/status - {task_id}.json', 'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data_res, ensure_ascii=False, indent=4)}')


if __name__ == '__main__':
    # asyncio.run(get_cards(archived=True))
    #
    # offer_id = 'SOVIET_RUGS-GA-6-37'
    # product_id = 1140830152
    # asyncio.run(get_card_info(offer_id, product_id))

    description_category_id = 17027906
    art = "Test-posters"
    data = {
        "items": [
            {
                "attributes": [
                    {
                        "complex_id": 0,
                        "id": 85,
                        "values": [
                            {
                                "dictionary_value_id": 971361449,
                                "value": "Стойка для акустической системы"
                            }
                        ]
                    },
                    {
                        "complex_id": 0,
                        "id": 8229,
                        "values": [
                            {
                                "dictionary_value_id": 91987,
                                "value": "Постер"
                            }
                        ]
                    },
                    {
                        "complex_id": 0,
                        "id": 9048,
                        "values": [
                            {
                                "value": "TESTALKFLSADF DJFKS DFJOEFJ E=фдщальшйош"
                            }
                        ]
                    },
                    {
                        "complex_id": 0,
                        "id": 11029,
                        "values": [
                            {
                                "value": "22"
                            }
                        ]
                    }
                ],
                "barcode": "6312772873170",
                "description_category_id": description_category_id,
                "color_image": "",
                "complex_attributes": [],
                "currency_code": "RUB",
                "depth": 10,
                "dimension_unit": "mm",
                "height": 250,
                "images": ["https://disk.yandex.ru/i/ci0YHDl_LknoLA"],
                "images360": [],
                "name": "тестовый арт. ВЫГРУЗКА!!!ВЫГРУЗКА!!!ARRRR",
                "offer_id": str(art),
                "old_price": "1100",
                "pdf_list": [],
                "price": "1000",
                "primary_image": "https://disk.yandex.ru/i/Hli7HgqOE094jA",
                "vat": "0.1",
                "weight": 100,
                "weight_unit": "g",
                "width": 150
            }
        ]
    }
    # asyncio.run(create_card(art, data))
    task_id = 1281849055
    asyncio.run(info_task_id(task_id))
