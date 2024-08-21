import json
import os

import pandas as pd
import requests
from loguru import logger
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

domain = 'http://127.0.0.1:8000/api_rest'


def get_products():
    url = f'{domain}/products-list'
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data
    else:
        logger.error(resp.status_code)
        logger.error(resp.text)


def chunks(lst, n):
    """Разбитие списка на чанки"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def create_json(file_path: str, data: list | dict | str) -> None:
    """Создание json файла"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as ex:
        logger.error(f"{file_path}\n{ex}")
    else:
        logger.success(f'Файл успешно создан: {file_path}')


def read_json(file_path: str) -> dict | list:
    """Чтение json файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as ex:
        logger.error(f"{file_path}\n{ex}")
    else:
        return data


def df_in_xlsx(df: pd.DataFrame, filename: str, directory: str = 'files', max_width: int = 50):
    """Запись датафрейма в файл"""
    workbook = Workbook()
    sheet = workbook.active
    for row in dataframe_to_rows(df, index=False, header=True):
        sheet.append(row)
    for column in sheet.columns:
        column_letter = column[0].column_letter
        max_length = max(len(str(cell.value)) for cell in column)
        adjusted_width = min(max_length + 2, max_width)
        sheet.column_dimensions[column_letter].width = adjusted_width

    os.makedirs(directory, exist_ok=True)
    workbook.save(f"{directory}\\{filename}.xlsx")
