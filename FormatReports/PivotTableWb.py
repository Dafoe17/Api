import pandas as pd
# import ToDatabase


def total_taxes(row):
    if row['ИП'] == 'Бонди':
        return row['Цена розничная с учетом согласованной скидки'] * 3 / 100
    else:
        return row['Цена розничная с учетом согласованной скидки'] * 7 / 100


def safe_division(row):
    if row['Количество'] != 0:
        return row['Количество (возвр)'] / row['Количество']
    else:
        return 0


def safe_division_2(row):
    if row['К перечислению Продавцу за реализованный Товар'] != 0:
        return row['Маржа'] / row['К перечислению Продавцу за реализованный Товар']
    else:
        return 0


def get(df, month, date):
    pivot_table_transf = df.pivot_table(index=['Тип Документа', 'Обоснования для оплаты', 'Виды логистики, штрафов и доплат'],
                                               values='К перечислению Продавцу за реализованный Товар',
                                               aggfunc='sum', fill_value=0)
    # ToDatabase.store_data(pivot_table, f'wb_tranf_table')

    # Логистика без вычета сторно, продажи
    filtered_df = df[(df['Тип Документа'] == 'Продажа') & (df['Количество возврата'] == 0)]
    pivot_table_1 = filtered_df.pivot_table(
        index=['Код номенклатуры'],
        values=['Услуги по доставке товара покупателю', 'Наименование'],
        aggfunc={'Услуги по доставке товара покупателю': ['sum', 'mean'], 'Наименование': 'count'}
    )
    print(pivot_table_1)
    pivot_table_1.columns = ['Сумма', 'Среднее', 'Количество']
    # ToDatabase.store_data(pivot_table_1, f'wb_layuot_{name}')

    # Логистика без вычета сторно, возвраты /отказы
    filtered_df = df[(df['Тип Документа'] == 'Продажа') & (df['Количество возврата'] == 1) & (
            df['Обоснования для оплаты'] == 'Логистика')]
    print(df)
    print(filtered_df)
    pivot_table_2 = filtered_df.pivot_table(
        index=['Код номенклатуры'],
        values=['Услуги по доставке товара покупателю', 'Количество возврата'],
        aggfunc={'Услуги по доставке товара покупателю': 'sum', 'Количество возврата': 'count'}
    )
    pivot_table_2.columns = ['Сумма', 'Количество (возвр)']
    pivot_table_2 = pd.concat([pivot_table_2, pivot_table_1['Количество']], axis=1)
    pivot_table_2 = pivot_table_2.fillna(0)
    pivot_table_2['Процент возврата'] = pivot_table_2.apply(safe_division, axis=1)
    temp_data = pivot_table_2['Количество'].sum() / pivot_table_1['Количество'].sum()
    print(temp_data)
    # ToDatabase.store_data(pivot_table_2, f'wb_layuot_Логистика без вычета сторно, возвраты /отказы')

    # Продажи
    filtered_df = df[(df['Тип Документа'] == 'Продажа') & (df['Количество возврата'] == 0) & (
            df['Обоснования для оплаты'] == 'Продажа')]
    pivot_table_3 = filtered_df.pivot_table(
        index=['Код номенклатуры'],
        values=['К перечислению Продавцу за реализованный Товар', 'Размер кВВ, %', '№'],
        aggfunc={'К перечислению Продавцу за реализованный Товар': 'sum', 'Размер кВВ, %': 'mean', '№': 'count'}
    )
    pivot_table_3.columns = ['Сумма', 'кВВ', 'Продажи, шт']
    print(pivot_table_3)
    # ToDatabase.store_data(pivot_table_3, f'wb_layuot_{name}')

    # Возврат
    filtered_df = df[(df['Тип Документа'] == 'Возврат') & (
            (df['Обоснования для оплаты'] == 'Возврат') | (df['Обоснования для оплаты'] == 'Сторно возврата'))]
    pivot_table_4 = filtered_df.pivot_table(
        index='Код номенклатуры',
        values=['К перечислению Продавцу за реализованный Товар', '№'],
        aggfunc={'К перечислению Продавцу за реализованный Товар': 'sum', '№': 'count'}
    )
    pivot_table_4.columns = ['Сумма', 'Количество']
    # ToDatabase.store_data(pivot_table_4, f'wb_layuot_Продажи')

    # Сторно логистика
    filtered_df = df[(df['Тип Документа'] == 'Возврат') & (df['Обоснования для оплаты'] == 'Продажа')]
    pivot_table_5 = filtered_df.pivot_table(
        index='Код номенклатуры',
        values='Услуги по доставке товара покупателю',
        aggfunc='sum'
    )
    # print(pivot_table_5)
    try:
        pivot_table_5.columns = ['Логистика сторно']
    except ValueError:
        pivot_table_5['Логистика сторно'] = 0
    # ToDatabase.store_data(pivot_table_5, f'wb_layuot_Сторно логистика')

    # Брак
    filtered_df = df[(df['Тип Документа'] == 'Продажа') & (df['Обоснования для оплаты'] == 'Возврат')]
    pivot_table_6 = filtered_df.pivot_table(
        index='Код номенклатуры',
        values='К перечислению Продавцу за реализованный Товар',
        aggfunc='sum'
    )
    try:
        pivot_table_6.columns = ['Возврат']
    except ValueError:
        pivot_table_6['Возврат'] = 0
    # ToDatabase.store_data(pivot_table_6, f'wb_layuot_Брак')

    # Сторно все
    filtered_df = df[(df['Тип Документа'] == 'Возврат') & ((df['Обоснования для оплаты'] == 'Сторно возвратов') | (
            df['Обоснования для оплаты'] == 'Сторно Продаж'))]
    pivot_table_7 = filtered_df.pivot_table(
        index='Код номенклатуры',
        values='К перечислению Продавцу за реализованный Товар',
        aggfunc='sum'
    )
    try:
        pivot_table_7.columns = ['Сумма']
    except ValueError:
        pivot_table_7['Сумма'] = 0
    # ToDatabase.store_data(pivot_table_7, f'wb_layuot_Сторно все')

    pivot_table_total = df.pivot_table(
        index=['Код номенклатуры'],
        values=['К перечислению Продавцу за реализованный Товар', 'Цена розничная с учетом согласованной скидки',
                'Услуги по доставке товара покупателю', 'Общая сумма штрафов', 'Доплаты', 'Закупочная цена',
                'Цена товара'],
        aggfunc={'К перечислению Продавцу за реализованный Товар': 'sum',
                 'Цена розничная с учетом согласованной скидки': 'sum',
                 'Услуги по доставке товара покупателю': 'sum',
                 'Общая сумма штрафов': 'sum', 'Доплаты': 'sum', 'Закупочная цена': 'mean', 'Цена товара': 'max'
                 }
    )
    print(pivot_table_total)
    pivot_table_total = pd.concat([pivot_table_total, df['ИП']])
    print(pivot_table_total)
    try:
        pivot_table_total = pd.concat([pivot_table_total, pivot_table_5])
        pivot_table_total = pivot_table_total['Логистика сторно'].fillna(0).astype(int)
    except TypeError:
        pivot_table_total['Логистика сторно'] = 0
    try:
        pivot_table_total = pd.concat([pivot_table_total, pivot_table_3['Продажи, шт']])
        pivot_table_total = pivot_table_total['Продажи, шт'].fillna(0).astype(int)
    except TypeError:
        pivot_table_total['Продажи, шт'] = 0
    try:
        pivot_table_total = pd.concat([pivot_table_total, pivot_table_6])
        pivot_table_total = pivot_table_total['Возрат'].fillna(0).astype(int)
    except TypeError:
        pivot_table_total['Возрат'] = 0
    pivot_table_total['Себестоимость'] = pivot_table_total['Закупочная цена'] * pivot_table_total['Продажи, шт']
    pivot_table_total['Маржа'] = pivot_table_total['К перечислению Продавцу за реализованный Товар'] - \
                                 pivot_table_total['Услуги по доставке товара покупателю'] - \
                                 pivot_table_total['Общая сумма штрафов'] - pivot_table_total['Доплаты'] - \
                                 pivot_table_total['Логистика сторно'] - pivot_table_total['Возрат'] - \
                                 pivot_table_total['Возрат'] - pivot_table_total['Себестоимость']
    pivot_table_total['Маржа (%)'] = pivot_table_total.apply(safe_division_2, axis=1)
    pivot_table_total['Стоимость товара'] = pivot_table_total['Продажи, шт'] * pivot_table_total['Цена товара']
    pivot_table_total['Налог'] = pivot_table_total.apply(total_taxes)
    # ToDatabase.store_data(pivot_table_total, f'wb_layuot_Итого')

    a = int(input('Введите удержание: '))
    b = int(input('Введите хранение: '))
    c = int(input('Введите самовыкупы: '))
    d = c * 0.18 + (55 + 35 + 100) * c / 800
    e = int(input('Введите внешнюю рекламу: '))
    f = int(input('Введите доп. потери: '))
    names = ['Сумма', 'Доля']
    data = {
        'Месяц': [month, month],
        'Неделя': [date, date],
        'Логистика': [pivot_table_total['Услуги по доставке товара покупателю'].sum(),
                      pivot_table_total['Услуги по доставке товара покупателю'].sum() / pivot_table_total[
                          'Цена розничная с учетом согласованной скидки'].sum()
                      if pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() != 0 else 0],
        'Комиссия': [pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() - pivot_table_total[
            'К перечислению Продавцу за реализованный Товар'].sum(),
                     pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() - pivot_table_total[
                         'К перечислению Продавцу за реализованный Товар'].sum()
                     / pivot_table_total['Цена розничная с учетом согласованной скидки'].sum()
                     if pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() != 0 else 0],
        'Склад+ЗП': [
            pivot_table_total['Себестоимость'].sum() - pivot_table_total['Стоимость товара'].sum() - pivot_table_total[
                'Налог'].sum(),
            pivot_table_total['Себестоимость'].sum() - pivot_table_total['Стоимость товара'].sum() -
            pivot_table_total['Налог'].sum() / pivot_table_total['Цена розничная с учетом согласованной скидки'].sum()
            if pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() != 0 else 0],
        'Товар': [pivot_table_total['Стоимость товара'].sum(),
                  pivot_table_total['Стоимость товара'].sum() / pivot_table_total[
                      'Цена розничная с учетом согласованной скидки'].sum()
                  if pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() != 0 else 0],
        'Маржа': [pivot_table_total['Маржа'] - (a + b + c + d + e + f),
                  pivot_table_total['Маржа'] - (a + b + c + d + e + f) / pivot_table_total['Цена розничная с учетом согласованной скидки'].sum()
                  if pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() != 0 else 0],
        'Продвижение': [a + d + e, (a + d + e) / pivot_table_total['Цена розничная с учетом согласованной скидки'].sum()
        if pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() != 0 else 0],
        'Хранение': [b, b / pivot_table_total['Цена розничная с учетом согласованной скидки'].sum()
        if pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() != 0 else 0],
        'Штрафы': [f + pivot_table_total['Общая сумма штрафов'].sum(),
                   (f + pivot_table_total['Общая сумма штрафов'].sum()) / pivot_table_total[
                       'Цена розничная с учетом согласованной скидки'].sum()
                   if pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() != 0 else 0],
        'Налоги': [pivot_table_total['Налог'].sum(),
                   pivot_table_total['Налог'].sum() / pivot_table_total[
                       'Цена розничная с учетом согласованной скидки'].sum()
                   if pivot_table_total['Цена розничная с учетом согласованной скидки'].sum() != 0 else 0]
    }
    df_result = pd.DataFrame(data=data, index=names)
    return df_result
