import asyncio
import json
import random
from pprint import pprint

import aiofiles
import aiohttp
from loguru import logger

from Api_ozon.db import Category, Characteristic, Parameter
from config import headers_ozon, categories_dict


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


async def create_card(data):
    """Создание карточки"""
    url = 'https://api-seller.ozon.ru/v3/product/import'
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.post(url, headers=headers_ozon, json=data) as response:
            print("Status:", response.status)
            data_res = await response.json()
            async with aiofiles.open(f'../files_ozon/push_cards.json', 'w', encoding='utf-8') as file:
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


def get_attributes(category, num, brand, name, descriptions, params):
    atrs = []

    required_atrs = Characteristic.select().where(Characteristic.category == category,
                                                  Characteristic.is_required == True)
    atrs.append({
        "id": 4191,
        "values": [
            {
                "value": descriptions
            }
        ]
    })
    for atr in required_atrs:
        if atr.id_ozon_character == 8229:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "dictionary_value_id": category.type_id
                    }
                ]
            })
        elif atr.id_ozon_character == 9048:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": "Выгрузка с срм"
                    }
                ]
            })

        elif atr.id_ozon_character == 85:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": brand
                    }
                ]
            })

        elif atr.id_ozon_character == 4180:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": name
                    }
                ]
            })
        elif atr.id_ozon_character == 6532:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": str(num)
                    }
                ]
            })
        elif atr.id_ozon_character == 6949:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": str(num)
                    }
                ]
            })

        elif atr.id_ozon_character == 11029:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": str(atr.default)
                    }
                ]
            })
        elif atr.id_ozon_character == 9163:
            items = atr.default.split(";")
            temp_atr = []
            for item in items:
                temp_atr.append({"value": item.strip()})
            atrs.append({
                "id": atr.id_ozon_character,
                "values": temp_atr
            })
        else:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": atr.default
                    }
                ]
            })
    not_required_atrs = Characteristic.select().where(Characteristic.category == category,
                                                      Characteristic.is_required == False, Characteristic.default != '')
    for atr in not_required_atrs:
        if ';' in atr.default:
            items = atr.default.split(";")
            temp_atr = []
            for item in items:
                temp_atr.append({"value": item.strip()})
            atrs.append({
                "id": atr.id_ozon_character,
                "values": temp_atr
            })
        else:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": str(atr.default) if atr.type == "String" else atr.default
                    }
                ]
            })
    not_required_atrs_and_not_default = Characteristic.select().where(Characteristic.category == category,
                                                                      Characteristic.is_required == False,
                                                                      Characteristic.default == '')
    for atr in not_required_atrs_and_not_default:
        if "Количество" in atr.name:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": str(num)
                    }
                ]
            })
        elif "Вес с упаковкой, г" in atr.name:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": str(params.weight)
                    }
                ]
            })
        elif "Вес товара, г" in atr.name:
            atrs.append({
                "id": atr.id_ozon_character,
                "values": [
                    {
                        "value": str(params.weight_product)
                    }
                ]
            })
    return atrs


if __name__ == '__main__':
    # asyncio.run(get_cards(archived=True))
    #
    # offer_id = 'SOVIET_RUGS-GA-6-37'
    # product_id = 1140830152
    # asyncio.run(get_card_info(offer_id, product_id)),

    category_name = "Значки"
    brand = 'Anikoya'
    # cat_list = [key for key, value in categories_dict.items() if 'набор' not in key]
    cat_list = ["Попсокеты"]
    num = 1

    data = {"items": []}
    for category_name in cat_list:
        if (category_name == "Значки" or category_name == "Кружки" or category_name == "Кружки-сердечко") and num > 1:
            category_name += "_набор"
        category = Category.get(Category.name == category_name)
        description_category_id = categories_dict[category_name].get('description_category_id')

        # Выгружать с вб
        art = f"Test-{category_name}"
        name = f"тестовый арт. {art}"
        barcode = str(random.randint(10 ** 11, 10 ** 12 - 1))
        descriptions = 'Описание Артикула'

        # Выгружать с яндекса
        images = ["https://disk.yandex.ru/i/ci0YHDl_LknoLA"]
        primary_image = "https://disk.yandex.ru/i/Hli7HgqOE094jA"
        try:
            parameters = Parameter.get(category=category, num=num)
        except:
            logger.error(f"{category_name} {num}")
            continue
        depth = parameters.depth
        height = parameters.height
        weight = parameters.weight
        width = parameters.width
        price = str(parameters.price)
        old_price = str(parameters.old_price)

        attributes = get_attributes(category, num, brand, name, descriptions, parameters)

        data['items'].append(
            {
                "attributes": attributes,
                "barcode": barcode,
                "description_category_id": description_category_id,
                "color_image": "",
                "complex_attributes": [],
                "currency_code": "RUB",
                "depth": depth,
                "dimension_unit": "mm",
                "height": height,
                "images": images,
                "images360": [],
                "name": name,
                "offer_id": art,
                "old_price": old_price,
                "pdf_list": [],
                "price": price,
                "primary_image": primary_image,
                "vat": "0",
                "weight": weight,
                "weight_unit": "g",
                "width": width
            }
        )
    pprint(data)
    # print(len(data["items"]))
    asyncio.run(create_card(data))
    # task_id = 1284298905
    # asyncio.run(info_task_id(task_id))
