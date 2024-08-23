from pathlib import Path

from environs import Env

env = Env()
env.read_env()
BASE_DIR = Path(__file__).resolve().parent

debug = True

api_key_wb_1 = env.str('token_1')
api_key_wb_2 = env.str('token_2')
api_key_wb_3 = env.str('token_3')
api_key_wb_4 = env.str('token_4')
api_key_wb_5 = env.str('token_5')
api_key_wb_6 = env.str('token_6')
api_key_wb_7 = env.str('token_7')
tokens_wb = [api_key_wb_1, api_key_wb_2, api_key_wb_3, api_key_wb_4, api_key_wb_5, api_key_wb_6, api_key_wb_7]
api_key_ozon = env.str('api_ozon_7')
client_id = env.str('client_id_7')

dict_lk = {
    1: 'FAVEGO',
    2: 'KOZEGO',
    3: 'MYCEGO',
    4: 'ULEGO',
    5: 'VBEGO',
    6: 'MEVEGO',
    7: 'GALEGO',
}

dict_tokens = {
    1: api_key_wb_1,
    2: api_key_wb_2,
    3: api_key_wb_3,
    4: api_key_wb_4,
    5: api_key_wb_5,
    6: api_key_wb_6,
    7: api_key_wb_7,
}


def get_headers_wb(token):
    headers_wb = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    return headers_wb


headers_ozon = {
    "Client-Id": client_id,
    "Api-Key": api_key_ozon
}

categories_dict = {
    "Значки": {"description_category_id": 17027899, "type_id": 93762, "ozon_category_name": "Значок"},
    "Значки_набор": {"description_category_id": 17027899, "type_id": 92853, "ozon_category_name": "Набор значков"},
    "Зеркальца": {"description_category_id": 17028985, "type_id": 93367, "ozon_category_name": "Зеркало карманное"},
    "Попсокеты": {"description_category_id": 17028922, "type_id": 268217788,
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
