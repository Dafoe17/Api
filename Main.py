from API import GetReports
from datetime import date, timedelta, datetime
import os
# import calendar
# from FormatReports import Formatting
# import pandas as pd

# Выгрузку по API совершает корректно (насколько позволяет Ozon, WB и МойСклад)
# С созданием сводных таблиц возникли проблемы (Formatting)


def check_and_create_temp_folder():
    if not os.path.exists('reports'):
        try:
            os.makedirs('reports')
            print("Папка 'reports' создана в корневой папке, в ней будут храниться отчеты по Wb, Ozon и МойСклад.")
        except OSError as e:
            print(f"Ошибка при создании папки 'temp': {e}")

    if not os.path.exists('reports/temp'):
        try:
            os.makedirs('reports/temp')
            print(
                "Папка 'temp' создана в папке 'reports', в ней будут временные данные (общий список товаров Wb, Ozon и МойСклад).")
        except OSError as e:
            print(f"Ошибка при создании папки 'temp': {e}")


def start_export(first_day, last_day):
    period, df_wb = GetReports.get_report_wb(first_day, last_day)
    df_ms = GetReports.get_report_mystore()
    df_oz = GetReports.get_report_ozon(period)

    # period = ['2023-07-03 — 2023-07-09']
    # df_wb = pd.read_csv('reports/temp/Wb.csv')
    # df_oz = pd.read_csv('reports/temp/Ozon.csv')
    # df_ms = pd.read_csv('reports/temp/MyStore.csv')
    # names = ['Сумма', 'Доля']
    # data = ['Месяц', 'Неделя', 'Логистика', 'Комиссия', 'Склад+ЗП', 'Товар', 'Маржа', 'Продвижение', 'Хранение', 'Штрафы', 'Налоги']
    # df_result = pd.DataFrame(data=[data], index=[names])
    # for x in period:
    #     print(f'Создаем сводные таблицы для недели: {x}')
    #     df_result = df_result.append(Formatting.pivot_tables_for_wb(df_wb, df_ms, x))
    #     df_result = df_result.append(Formatting.pivot_tables_for_ozon(df_oz, df_ms, x))
    # Formatting.format_cvs(df_result, datetime.now().month)


today = date.today()
f_day = date(today.year, today.month, 1)
l_day = date(today.year, today.month + 1, 1) - timedelta(days=1)

check_and_create_temp_folder()
start_export(f_day, l_day)


