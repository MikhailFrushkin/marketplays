import asyncio
import json

import aiofiles
import aiohttp
import pandas as pd

from config import headers_ozon, BASE_DIR
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
            async with aiofiles.open(f'{BASE_DIR}/files_ozon/search_manual-{string}.json',
                                     'w', encoding='utf-8') as file:
                await file.write(f'{json.dumps(data, ensure_ascii=False, indent=4)}')


def export_to_excel():
    # Создаем объект ExcelWriter для записи на разные листы
    with pd.ExcelWriter('categories_characteristics.xlsx') as writer:
        # Проходим по каждой категории
        for category in Category.select():
            # Извлекаем характеристики, связанные с данной категорией
            characteristics = Characteristic.select().where(Characteristic.category == category)

            # Преобразуем данные в DataFrame для удобной записи в Excel
            data = []
            for characteristic in characteristics:
                data.append({
                    'id_ozon_character': characteristic.id_ozon_character,
                    'name': characteristic.name,
                    'description': characteristic.description,
                    'type': characteristic.type,
                    'is_collection': characteristic.is_collection,
                    'is_required': characteristic.is_required,
                    'dictionary_id': characteristic.dictionary_id,
                    'max_value_count': characteristic.max_value_count
                })

            # Если есть данные, записываем их на соответствующий лист
            if data:
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name=category.name, index=False)
            else:
                # Если у категории нет характеристик, записываем пустой лист
                pd.DataFrame().to_excel(writer, sheet_name=category.name)

    print("Данные успешно записаны в Excel-файл.")


if __name__ == '__main__':
    categories_dict = {
        "Значки": {"description_category_id": 17027899, "type_id": 93762, "ozon_category_name": "Значок"},
        "Значки_набор": {"description_category_id": 17027899, "type_id": 92853, "ozon_category_name": "Набор значков"},
        "Зеркальца": {"description_category_id": 17028985, "type_id": 93367, "ozon_category_name": "Зеркало карманное"},
        "Попсокеты": {"description_category_id": 200001226, "type_id": 268217788,
                      "ozon_category_name": "Попсокет/кольцо для телефона"},
        "Постеры": {"description_category_id": 17027906, "type_id": 91987, "ozon_category_name": "Постер"},
        "Мини постеры": {"description_category_id": 17027906, "type_id": 91987, "ozon_category_name": "Постер"},
        "Кружки": {"description_category_id": 17028741, "type_id": 92499, "ozon_category_name": "Кружка"},
        "Кружки_набор": {"description_category_id": 17028741, "type_id": 367159078, "ozon_category_name": "Набор кружек"},
        "Кружки-сердечко": {"description_category_id": 17028741, "type_id": 92499, "ozon_category_name": "Кружка"},
        "Кружки-сердечко_набор": {"description_category_id": 17028741, "type_id": 367159078,
                             "ozon_category_name": "Набор кружек"},
        "Наклейки квадратные": {"description_category_id": 17029018, "type_id": 971123837,
                                "ozon_category_name": "Наклейка-памятка"},
        "Наклейки на карту": {"description_category_id": 17029018, "type_id": 971123837,
                              "ozon_category_name": "Наклейка-памятка"},
        "Наклейки на окна": {"description_category_id": 17029018, "type_id": 971123837,
                             "ozon_category_name": "Наклейка-памятка"},
        "Стикерпаки": {"description_category_id": 17029018, "type_id": 971123837,
                       "ozon_category_name": "Наклейка-памятка"},
        "Наклейки 3-D": {"description_category_id": 17028628, "type_id": 91561,
                         "ozon_category_name": "Наклейка на смартфон/планшет"},
        "Спортивные бутылки": {"description_category_id": 17027926, "type_id": 91941,
                               "ozon_category_name": "Декоративная бутылка"},
        "Маски": {"description_category_id": 17028733, "type_id": 95428, "ozon_category_name": "Маска карнавальная"},
        "Брелки": {"description_category_id": 17027899, "type_id": 87458885, "ozon_category_name": "Брелок"},
        "Коврики для мыши": {"description_category_id": 18262715, "type_id": 96808,
                             "ozon_category_name": "Коврик для мыши"},
    }
    description_category_id = 17027906
    type_id = 91987
    attribute_id = 11029
    string = 'anikoya'

    # asyncio.run(get_categories_ozon())
    # asyncio.run(get_characters_ozon(description_category_id, type_id))
    # asyncio.run(get_manual_characters_ozon(description_category_id, type_id, attribute_id))
    # asyncio.run(search_manual(description_category_id, type_id, attribute_id, string))

    # for cat, value in categories_dict.items():
    #     category = Category.create(name=cat, description_category_id=value["description_category_id"], type_id=value["type_id"],
    #                                ozon_category_name=value["ozon_category_name"])

    # categories = Category.select()
    # for cat in categories:
    #     data = asyncio.run(get_characters_ozon(cat.description_category_id, cat.type_id))
    #     for item in data["result"]:
    #         Characteristic.get_or_create(
    #             category=cat,
    #             id_ozon_character=item['id'],
    #             name=item['name'],
    #             description=item['description'],
    #             type=item['type'],
    #             is_collection=item['is_collection'],
    #             is_required=item['is_required'],
    #             dictionary_id=item['dictionary_id'],
    #             max_value_count=item.get('max_value_count', None),
    #         )
    export_to_excel()
