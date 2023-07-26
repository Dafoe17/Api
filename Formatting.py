import pandas as pd
# import ToDatabase
from FormatReports import PivotTableWb
from datetime import datetime
import calendar
import locale

# Тут проблема с конкатами, нужно чтобы он сравнивал индексы со столбцом "Код" (я это не делал)

locale.setlocale(locale.LC_TIME, 'ru_RU')


def calculate_total(row):
    try:
        result = (row['Цена: Цена закупки в юанях'] * 1.01 + row['Вес'] * row[
            'Доп. поле: Логистика (Кит-Мск)']) * 12
        return result
    except TypeError:
        return 0


def pivot_tables_for_wb(df_wb, df_mc, date):
    df_wb['Площадка'] = 'WB'
    df_wb = df_wb[(df_wb['Период'] == date)]
    date_from, date_to = date.split(" — ")
    month_from = datetime.strptime(date_from, '%Y-%m-%d').month
    month_to = datetime.strptime(date_to, '%Y-%m-%d').month
    if month_from != month_to:
        month = calendar.month_name[month_from] + " - " + calendar.month_name[month_to]
    else:
        month = calendar.month_name[month_from]
    df_wb['Месяц'] = month

    df_mc = df_mc[['Группы', 'Код', 'Наименование', 'Артикул', 'Цена: Цена закупки в юанях', 'Закупочная цена',
                   'Штрихкод EAN8', 'Вес', 'Доп. поле: Артикул на сайте WB', 'Доп. поле: ABC анализ',
                   'Доп. поле: Логистика (Кит-Мск)', 'Доп. поле: Дата поступления первого остатка', 'Остаток']]

    def vlookupc_logistics(value):
        try:
            result = df_mc.loc[df_mc['Артикул'] == value, 'Доп. поле: Логистика (Кит-Мск)'].values[0]
            return result
        except IndexError:
            return 35

    df_mc['Доп. поле: Логистика (Кит-Мск)'] = df_mc['Артикул'].apply(vlookupc_logistics)

    columns_to_replace = ['Цена: Цена закупки в юанях', 'Вес', 'Доп. поле: Логистика (Кит-Мск)']
    df_mc[columns_to_replace] = df_mc[columns_to_replace].replace('', '0').replace(',', '.', regex=True).astype(float)
    df_mc['Итого'] = df_mc.apply(calculate_total, axis=1)

    df_mc.columns = ['Группа', 'Код', 'Наименование', 'Артикул', 'Цена закупки в юанях', 'Закупочная цена',
                     'Штрихкод EAN8', 'Вес', 'Артикул на сайте WB', 'ABC анализ', 'Логистика (Кит-Мск)',
                     'Дата поступления первого остатка', 'Остаток', 'Цена товара']

    df = pd.merge(df_wb, df_mc, on='Артикул')
    columns_to_replace = ['Количество возврата', 'Услуги по доставке товара покупателю', 'Размер кВВ, %',
                          'К перечислению Продавцу за реализованный Товар',
                          'Цена розничная с учетом согласованной скидки', 'Общая сумма штрафов', 'Доплаты',
                          'Закупочная цена',
                          'Цена товара']
    df[columns_to_replace] = df[columns_to_replace].replace('', '0').replace(',', '.', regex=True).astype(float)
    df = pd.concat(PivotTableWb.get(df, month, date), df_wb[['Месяц', 'Период', 'Площадка']], ignore_index=True)
    return df


def pivot_tables_for_ozon(df_oz, df_mc, date):
    df_oz['Площадка'] = 'Ozon'
    df_oz = df_oz[(df_oz['Период'] == date)]
    month = datetime.strptime(date, "%d/%m/%Y").month
    month = calendar.month_name[month]
    df_oz['Месяц'] = month

    df_mc = df_mc[['Группы', 'Код', 'Наименование', 'Артикул', 'Цена: Цена закупки в юанях', 'Закупочная цена',
                   'Штрихкод EAN8', 'Вес', 'Доп. поле: Артикул на сайте WB', 'Доп. поле: ABC анализ',
                   'Доп. поле: Логистика (Кит-Мск)', 'Доп. поле: Дата поступления первого остатка', 'Остаток']]

    columns_to_replace = ['Цена: Цена закупки в юанях', 'Вес', 'Доп. поле: Логистика (Кит-Мск)']
    df_mc[columns_to_replace] = df_mc[columns_to_replace].replace('', '0').replace(',', '.', regex=True).astype(float)
    df_mc['Итого'] = df_mc.apply(calculate_total, axis=1)

    df_mc.columns = ['Группа', 'Код', 'Наименование', 'Артикул', 'Цена закупки в юанях', 'Закупочная цена',
                     'Штрихкод EAN8', 'Вес', 'Артикул на сайте WB', 'ABC анализ', 'Логистика (Кит-Мск)',
                     'Дата поступления первого остатка', 'Остаток', 'Цена товара']

    df = pd.merge(df_oz, df_mc, on='Артикул')
    columns_to_replace = ['Количество возврата', 'Услуги по доставке товара покупателю', 'Размер кВВ, %',
                          'К перечислению Продавцу за реализованный Товар',
                          'Цена розничная с учетом согласованной скидки', 'Общая сумма штрафов', 'Доплаты',
                          'Закупочная цена',
                          'Цена товара']
    df[columns_to_replace] = df[columns_to_replace].replace('', '0').replace(',', '.', regex=True).astype(float)
    df = pd.concat(PivotTableWb.get(df, month, date), df_oz[['Месяц', 'Период', 'Площадка']], ignore_index=True)
    return df


def format_cvs(df_to_cvs, month):
    csv_path = f'reports/temp/{month}.Total.csv'
    df_to_cvs.to_csv(csv_path, header=True, index=False)
