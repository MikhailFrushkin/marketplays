import glob
from pprint import pprint

import pandas as pd
from loguru import logger

from config import BASE_DIR
from utils import df_in_xlsx, read_json, create_json, get_products


def get_barcodes(target_index: list[str]):
    lk_dict = {
        "1": 'Филиппов А.В',
        "2": 'Козорез Д.О.',
        "3": 'Мосунов Я.С.',
        "4": 'Филиппова Ю.В.',
        "5": 'Филиппов В.Б',
        "6": 'Мосунова Е.В.',
        "7": 'Марущак Г.А.',
    }
    data_tuple = list()
    files_data_wb = glob.glob(f'{BASE_DIR}/files_wb/wildberries_data_cards*')
    for index, file in enumerate(files_data_wb, start=1):
        index_lk = file.split('_')[-1].replace('.json', '')
        if index_lk not in target_index:
            continue
        data = read_json(file)
        if not data:
            logger.error(f'Не получилось загрузить данные из файла: {file}')
            continue
        else:
            for item in data:
                try:
                    photo = item['photos'][0]['c246x328']
                except Exception as ex:
                    logger.error(f'{item["vendorCode"]} - {ex}')
                    photo = ''
                data_tuple.append(
                    (item['vendorCode'], item['nmID'], lk_dict[index_lk], item['brand'], item['subjectName'],
                     item['sizes'][0]['skus'][0], photo, item['updatedAt'].split('T')[0]))
    df = pd.DataFrame(data_tuple,
                      columns=['Артикул', 'Артикул вб', 'Кабинет', 'Брэнд', 'Категория', 'Баркод', 'Фото', 'Обновлен'])
    df_in_xlsx(df, 'Баркоды')
    create_json('result.json', data_tuple)


def create_old_arts(categories_wb: list, site_data):
    arts_list_wb = []
    files_data_wb = glob.glob(f'{BASE_DIR}/files_wb/wildberries_data_cards*')
    for index, file in enumerate(files_data_wb, start=1):
        data_wb_lk = read_json(file)
        for key in data_wb_lk:
            if key["subjectName"] in categories_wb:
                arts_list_wb.append(key['vendorCode'].strip().replace(' ', '').replace('\n', '').replace('\t', ''))
        print(len(arts_list_wb))

    art_no_task = []
    for art in arts_list_wb:
        try:
            data_art = data[art]
        except Exception as ex:
            if "_DP" not in art and "ULEGO" not in art:
                art_no_task.append(art)
            logger.error(art)
        else:
            # if data_art['task']['title'] == "Создание артикула из старой базы" and not data_art['art_in_base']:
            if not data_art['art_in_base']:
                if "_DP" not in art and "ULEGO" not in art:
                    art_no_task.append(art)

    for i in art_no_task:
        print(i)
    create_json('files\\auto_task.json', art_no_task)
    df = pd.DataFrame(art_no_task, columns=['Артикул'])
    df_in_xlsx(df, ','.join(categories_wb))
    print(len(art_no_task))


if __name__ == '__main__':
    # data_site = get_products()
    # create_json('files\\site_data_tasks.json', data_site)
    #
    categories_wb = ["Значки"]
    data = read_json('files\\site_data_tasks.json')
    create_old_arts(categories_wb, data)
