import asyncio

import pandas as pd

from Api_ozon.characters_ozon import get_characters_ozon
from Api_ozon.db import Category, Characteristic, Parameter
from config import categories_dict


def export_to_excel():
    # Создаем объект ExcelWriter для записи на разные листы
    with pd.ExcelWriter('categories_characteristics_null.xlsx') as writer:
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


def create_cat_character_base():
    for cat, value in categories_dict.items():
        Category.get_or_create(name=cat, description_category_id=value["description_category_id"],
                        type_id=value["type_id"],
                        ozon_category_name=value["ozon_category_name"])

    categories = Category.select()
    for cat in categories:
        data = asyncio.run(get_characters_ozon(cat.description_category_id, cat.type_id))
        for item in data["result"]:
            Characteristic.get_or_create(
                category=cat,
                id_ozon_character=item['id'],
                name=item['name'],
                description=item['description'],
                type=item['type'],
                is_collection=item['is_collection'],
                is_required=item['is_required'],
                dictionary_id=item['dictionary_id'],
                max_value_count=item.get('max_value_count', None),
            )
    # export_to_excel()

    categories = Category.select()
    for cat in categories:
        df = pd.read_excel("categories_characteristics.xlsx", sheet_name=cat.name).fillna("")
        for index, row in df.iterrows():
            character = Characteristic.get(category=cat, id_ozon_character=row["id_ozon_character"], name=row["name"])
            character.default = row["default"] if (row["default"] != 'nan' or row["default"] != 'Nan'
                                                   or row["default"] != "" or not row["default"]) else None
            character.save()


def push_parameters_base():
    df = pd.read_excel('Габаритыи цены.xlsx').fillna("")
    column_list = [i.strip() for i in df.columns if "Unnamed" not in i]
    print(column_list)

    for index, column in enumerate(column_list):
        try:
            category_name, size = column.split('_')
        except:
            category_name, size = column, column
        index_row = index * 5 + 1
        for x in range(1, 201):
            num = x
            weight_product = df.iloc[x, index_row]
            if not weight_product:
                continue
            weight = df.iloc[x, index_row + 1]
            parameters = df.iloc[x, index_row + 2]
            price = df.iloc[x, index_row + 4]
            if price:
                old_price = str(int(price + 200))
            else:
                continue
            if parameters:
                width, depth, height = parameters.split("*")
            else:
                continue
            if (
                    category_name == "Значки" or category_name == "Кружки" or category_name == "Кружки-сердечко") and num > 1:
                category_name += "_набор"
            category = Category.get(Category.name == category_name)
            print(category)
            Parameter.get_or_create(
                category=category,
                name=column,
                num=num,
                size=size,
                width=width,
                depth=depth,
                height=height,
                weight=weight,
                weight_product=weight_product,
                price=price,
                old_price=old_price,
            )


if __name__ == '__main__':
    # create_cat_character_base()
    push_parameters_base()
