import requests
import pandas as pd
from API import WB
from API import Ozon
from API import MyStore
import json
from datetime import datetime
# import ToDatabase


def get_report_wb(date_from, date_to):
    print("Выгружаем данные с WB (Бонди)...")
    wb_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' \
               '.eyJhY2Nlc3NJRCI6IjJhODkzYmQ1LWY5OWQtNDg4YS1iYTRlLTUxOGJmNGVkYTg5MCJ9' \
               '.0EoP3y_qssvDInK0TYwESo7cTitAb7Bxoho3o5pXUxM'
    wb_url = 'https://statistics-api.wildberries.ru/api/v1/supplier/reportDetailByPeriod'
    const = {'Authorization': wb_token}
    query = {'dateFrom': date_from,  # В формате ZZZZ-MM-DD
             'dateTo': date_to,
             'rrdid': 0}
    response = requests.get(wb_url, headers=const, params=query)
    json_data_1 = response.json()
    print(response)
    print("Выгружаем данные с WB (Эккель)...")
    wb_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' \
               '.eyJhY2Nlc3NJRCI6Ijg2ZDc0ZjU5LWM1Y2UtNGJiNi1hZThkLWE4MGU2MThkNDMyYSJ9' \
               '.e6qW06JGxDLQOEUb7fMm8JS8vL6tz33w_NYpCzp2zIY'
    const = {'Authorization': wb_token}
    response = requests.get(wb_url, headers=const, params=query)
    json_data_2 = response.json()
    print(response)
    df_1, period_array = WB.format_report(json_data_1, 'Бонди')
    df_2, period_array = WB.format_report(json_data_2, 'Эккель')
    df = df_1.append(df_2)
    # ToDatabase.store_data(df, 'Wb')
    return period_array, df


def get_report_mystore():
    print('Выгружаем данные с Мой Склад...')
    my_store_token = 'eca291442d32de91814d643f329ff94b0ab0ea1e'
    my_store_url = 'https://online.moysklad.ru/api/remap/1.2/entity/product'
    const = {'Authorization': my_store_token}
    x = 0
    query = {'groupBy': 'product',
             'offset': x}
    response = requests.get(my_store_url, headers=const, params=query)
    json_data = response.json()
    df = MyStore.format_report(json_data)
    df_upd = df
    while MyStore.check(df_upd):
        x += 1000
        query = {'groupBy': 'product',
                 'offset': x}
        response = requests.get(my_store_url, headers=const, params=query)
        json_data = response.json()
        df_upd = MyStore.format_report(json_data)
        df = df.append(df_upd)
    MyStore.format_cvs(df)
    # ToDatabase.store_data(df, "MyStore")
    return df


def get_report_ozon(period):
    print('Выгружаем данные с Ozon...')
    df = pd.DataFrame()
    for date in period:
        print('Период: ', date)
        date_from, date_to = date.split(" — ")
        date_from = datetime.strptime(date_from, '%Y-%m-%d').strftime('%Y-%m-%dT00:00:00.000Z')
        date_to = datetime.strptime(date_to, '%Y-%m-%d').strftime('%Y-%m-%dT00:00:00.000Z')
        x = 1
        ozon_token = '232631f9-e084-44bc-a92e-01b845fd3479'
        ozon_client_id = '182899'
        ozon_url = 'https://api-seller.ozon.ru/v3/finance/transaction/list'
        const = {"Client-Id": ozon_client_id,
                 "Api-Key": ozon_token}
        body = {
            "filter": {
                "date": {
                    "from": date_from,
                    "to": date_to
                },
                "operation_type": [],
                "posting_number": "",
                "transaction_type": "all"
            },
            "page": x,
            "page_size": 1000
        }
        body = json.dumps(body)
        response = requests.post(ozon_url, headers=const, data=body)
        json_data = response.json()
        print(response)
        df_upd = Ozon.format_report(json_data, date)
        while Ozon.check(df_upd):
            x += 1
            body = {
                "filter": {
                    "date": {
                        "from": date_from,
                        "to": date_to
                    },
                    "operation_type": [],
                    "posting_number": "",
                    "transaction_type": "all"
                },
                "page": x,
                "page_size": 1000
            }
            body = json.dumps(body)
            response = requests.post(ozon_url, headers=const, data=body)
            json_data = response.json()
            df_upd = Ozon.format_report(json_data, date)
            df = df.append(df_upd)
    Ozon.format_cvs(df)
    # ToDatabase.store_data(df.astype(str), "Ozon")
    return df

# Большинство артикулов озон не выдает почему-то


def get_article_ozon(sku):
    print('Выгружаем артикулы Ozon товаров...')
    ozon_token = '232631f9-e084-44bc-a92e-01b845fd3479'
    ozon_client_id = '182899'
    ozon_url = 'https://api-seller.ozon.ru/v2/product/info/list'
    sku = [str(element) for element in sku]
    sku = [element for element in sku if element != ""]
    const = {"Client-Id": ozon_client_id,
             "Api-Key": ozon_token}
    body = {
        "offer_id": [],
        "product_id": [],
        "sku": sku
    }
    body = json.dumps(body)
    response = requests.post(ozon_url, headers=const, data=body)
    json_data = response.json()
    # json_string = json.dumps(json_data)
    # print(json_string)
    df_article = Ozon.format_article(json_data)
    return df_article
