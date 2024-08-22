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
