import pandas as pd

from utils import create_json, read_json, df_in_xlsx


def new_site_data():
    result = {}
    data_json = read_json('files\\site_data.json')
    for key, value in data_json.items():
        result[value['art']] = key

    create_json('files\\result_art_data.json', result)


def update_art():
    df = pd.read_excel('files\\Баркоды.xlsx')
    arts_dict: dict = read_json('files\\site_data.json')
    count = 0
    result_data = []
    bad_arts = {}
    categories = ['Постеры', 'Кольца-держатели для телефона', 'Значки', 'Плакаты', 'Бутылки для воды', 'Кружки',
                  'Коврики для мыши', 'Зеркальца', 'Стикеры']
    for index, row in df.iterrows():
        article = row['Артикул'].strip().replace(' ', '').replace('\n', '').replace('\t', '')
        if article in arts_dict:
            result_data.append((arts_dict[article], article, row['Артикул вб'], str(row['Баркод']), row['Фото'],))
        else:
            if row['Категория'] in categories:
                if row['Категория'] in bad_arts:
                    bad_arts[row['Категория']]['arts'].append(row['Артикул'])
                    bad_arts[row['Категория']]['count'] += 1
                else:
                    bad_arts[row['Категория']] = {'arts': [row['Артикул']], 'count': 1}
                count += 1
    print(f'Не найдено артикулов {count}')
    df = pd.DataFrame(result_data, columns=['id', 'art', 'art_wb', 'barcode', 'preview'])
    df_in_xlsx(df, 'push_data.xlsx', 'files')
    create_json('files\\bad_arts.json', bad_arts)


if __name__ == '__main__':
    # data = get_products()
    # create_json('files\\site_data.json', data)
    update_art()
