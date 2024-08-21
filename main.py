import glob
import json

from loguru import logger

from config import BASE_DIR, dict_lk, dict_tokens
from utils import create_json, read_json


def create_data_wb_cards(data_wb):
    bad_fields = ('photos', 'createdAt', 'updatedAt', 'imtID', 'subjectName', 'subjectID', 'nmUUID')
    for item in data_wb:
        for field in bad_fields:
            try:
                del item[field]
            except Exception as ex:
                pass
                # print(item['vendorCode'])
        try:
            del item['dimensions']['isValid']
        except Exception as ex:
            logger.error(ex)
    # create_json(f'{BASE_DIR}/files_wb/result_cards_wb.json', 'w', data_wb)
    return data_wb


def get_brands(file_name):
    brands = set()
    with open(file_name, 'r', encoding='utf-8') as file:
        data_cads: list = json.load(file)
    for item in data_cads:
        brands.add(item['brand'])
    return list(brands)


def get_bad_brands_card(data_wb):
    bad_data = []
    for item in data_wb:
        if item['brand'] not in good_brands:
            # print(item['vendorCode'])
            bad_data.append(item)
    return bad_data


def create_update_data(target_index_lk):
    replace_data = {
        'lamark line': 'Lamark Line2',
        'дочке понравилось': 'Дочке понравилось2',
        'Дочке Понравилось': 'Дочке понравилось2',
        'posuta': 'POSUTA2',
        'Posuta': 'POSUTA2',
        'anikoya': 'AniKoya2',
        'АniKoya': 'AniKoya2',
        'Anikoya': 'AniKoya2',
        'АniKoyа': 'AniKoya2',
        'POSUTA2': 'POSUTA2',
        'Дочке понравилось2': 'Дочке понравилось2',
    }
    replace_data2 = {
        'lamark line': 'Lamark Line',
        'дочке понравилось': 'Дочке понравилось',
        'Дочке Понравилось': 'Дочке понравилось',
        'posuta': 'POSUTA',
        'Posuta': 'POSUTA',
        'anikoya': 'AniKoya',
        'АniKoya': 'AniKoya',
        'Anikoya': 'AniKoya',
        'АniKoyа': 'AniKoya',
        'POSUTA2': 'POSUTA',
        'Дочке понравилось2': 'Дочке понравилось',
    }
    files_data_wb = glob.glob(f'{BASE_DIR}/files_wb/wildberries_data_cards*')
    for index, file in enumerate(files_data_wb, start=1):
        if index == target_index_lk:
            data = read_json(file)
            if not data:
                logger.error(f'Не получилось загрузить данные из файла: {file}')
                continue
            data_cards = create_data_wb_cards(data)
            brands = get_brands(file)
            print(brands)
            bad_data_result = get_bad_brands_card(data_cards)
            print(dict_lk[index], len(bad_data_result))
            push_data = []
            for item in bad_data_result:
                if item['brand'] in replace_data:
                    item['brand'] = replace_data2[item['brand']]
                    push_data.append(item)
                else:
                    logger.error(item)
            create_json(f'{BASE_DIR}/files_wb/result_push_data_{index}.json', push_data)


if __name__ == '__main__':
    good_brands = ['Bidjo', 'POSUTA', 'AniKoya', 'Дочке понравилось', 'POSTERDOM', 'Jibb', 'TATMART', 'MyMake',
                   'CAR-ABS', 'МицелВит', 'MyMake', 'Lamark Line']
    create_update_data(1)