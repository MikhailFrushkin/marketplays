import asyncio
import json

import aiofiles
import aiohttp
import pandas as pd

from config import headers_ozon, BASE_DIR, categories_dict
from db import Category, Characteristic, db


async def get_categories_ozon():
    """Возвращает категории и типы для товаров в виде дерева"""
    url = 'https://api-seller.ozon.ru/v1/description-category/tree'
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.post(url, headers=headers_ozon, json={'language': 'RU'}) as response:
            print("Status:", response.status)
            data = await response.json()
            async with aiofiles.open(f'{BASE_DIR}/files_ozon/tree_category.json', 'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data, ensure_ascii=False, indent=4)}')


async def get_characters_ozon(description_category_id, type_id):
    """Получение характеристик для указанной категории и типа товара"""
    url = 'https://api-seller.ozon.ru/v1/description-category/attribute'
    json_data = {
        "description_category_id": description_category_id,
        "language": "DEFAULT",
        "type_id": type_id
    }
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.post(url, headers=headers_ozon, json=json_data) as response:
            print("Status:", response.status)
            data_res = await response.json()
            async with aiofiles.open(f'{BASE_DIR}/files_ozon/character-{description_category_id}-{type_id}.json', 'w',
                                     encoding='utf-8') as file:
                await file.write(f'{json.dumps(data_res, ensure_ascii=False, indent=4)}')
    return data_res


async def get_manual_characters_ozon(description_category_id, type_id, attribute_id):
    """Справочник значений характеристики"""
    url = 'https://api-seller.ozon.ru/v1/description-category/attribute/values'
    json_data = {
        "attribute_id": attribute_id,
        "description_category_id": description_category_id,
        "language": "DEFAULT",
        "last_value_id": 0,
        "limit": 5000,
        "type_id": type_id
    }
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.post(url, headers=headers_ozon, json=json_data) as response:
            print("Status:", response.status)
            data = await response.json()
            async with aiofiles.open(
                    f'{BASE_DIR}/files_ozon/manual-{description_category_id}-{type_id}-{attribute_id}.json',
                    'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data, ensure_ascii=False, indent=4)}')


async def search_manual(description_category_id, type_id, attribute_id, string):
    """Поиск по справочным значениям характеристики"""
    url = 'https://api-seller.ozon.ru/v1/description-category/attribute/values/search'
    json_data = {
        "attribute_id": attribute_id,
        "description_category_id": description_category_id,
        "limit": 100,
        "type_id": type_id,
        "value": string
    }
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.post(url, headers=headers_ozon, json=json_data) as response:
            print("Status:", response.status)
            data = await response.json()
            async with aiofiles.open(f'{BASE_DIR}/files_ozon/search_manual-1.json',
                                     'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data, ensure_ascii=False, indent=4)}')




if __name__ == '__main__':
    description_category_id = 17027899
    type_id = 93762
    attribute_id = 5308
    string = 'Попсоке'

    asyncio.run(get_categories_ozon())
    # asyncio.run(get_characters_ozon(description_category_id, type_id))
    # asyncio.run(get_manual_characters_ozon(description_category_id, type_id, attribute_id))
    # asyncio.run(search_manual(description_category_id, type_id, attribute_id, string))
