import pandas as pd
# import ToDatabase


def total_taxes(row):
    if row['ИП'] == 'Бонди':
        return row['За продажу или возврат до вычета комиссий и услуг'] * 3 / 100
    else:
        return row['За продажу или возврат до вычета комиссий и услуг'] * 7 / 100


def safe_division(row):
    if row['Итого'] != 0:
        return row['Маржа'] / row['Итого']
    else:
        return 0


def get(df, month, date):
    pivot_table_transf = df(
        index=['Тип начисления'],
        values=['Итого', 'За продажу или возврат до вычета комиссий и услуг', 'Комиссия за продажу', 'Логистика'],
        aggfunc='sum'
    )

    filtered_df = df[(df['Тип начисления'] == 'Доставка и обработка возврата, отмены, невыкупа') |
                     (df['Тип начисления'] == 'Получение возврата, отмены, невыкупа от покупателя') |
                     (df['Тип начисления'] == 'Доставка покупателю — отмена начисления')]
    pivot_table_transf_1 = filtered_df(
        index=['Тип начисления'],
        values=['Итого', 'За продажу или возврат до вычета комиссий и услуг', 'Комиссия за продажу', 'Логистика'],
        aggfunc='sum'
    )

    filtered_df = df[(df['Тип начисления'] == 'Услуга размещения товаров на складе')]
    pivot_table_transf_2 = filtered_df(
        index=['Тип начисления'],
        values=['Итого', 'За продажу или возврат до вычета комиссий и услуг', 'Комиссия за продажу', 'Логистика'],
        aggfunc='sum'
    )

    filtered_df = df[(df['Тип начисления'] == 'Начисление за хранение/утилизацию возвратов')]
    pivot_table_transf_3 = filtered_df(
        index=['Тип начисления'],
        values=['Итого', 'За продажу или возврат до вычета комиссий и услуг', 'Комиссия за продажу', 'Логистика'],
        aggfunc='sum'
    )

    filtered_df = df[(df['Тип начисления'] == 'Обработка неопознанных излишков с приемки') |
                     (df['Тип начисления'] == 'Утилизация') |
                     (df['Тип начисления'] == 'Бронирование места для размещения на складе') |
                     (df['Тип начисления'] == 'Доставка товаров на склад Ozon (кросс-докинг)')]
    pivot_table_transf_4 = filtered_df(
        index=['Тип начисления'],
        values=['Итого', 'За продажу или возврат до вычета комиссий и услуг', 'Комиссия за продажу', 'Логистика'],
        aggfunc='sum'
    )

    filtered_df = df[(df['Тип начисления'] == 'Услуги продвижения товаров') |
                     (df['Тип начисления'] == 'Premium-подписка') |
                     (df['Тип начисления'] == 'Услуга продвижения Бонусы продавца')]
    pivot_table_transf_5 = filtered_df(
        index=['Тип начисления'],
        values=['Итого', 'За продажу или возврат до вычета комиссий и услуг', 'Комиссия за продажу', 'Логистика'],
        aggfunc='sum'
    )

    # Логистика, возвраты /отказы
    filtered_df = df[(df['Тип начисления'] == 'Доставка и обработка возврата, отмены, невыкупа') |
                     (df['Тип начисления'] == 'Начисление за хранение/утилизацию возвратов') |
                     (df['Тип начисления'] == 'Получение возврата, отмены, невыкупа от покупателя')]
    pivot_table_1 = filtered_df.pivot_table(
        index='Код',
        values=['Количество', 'Обратная логистика', 'Обработка невыкупленного товара', 'Магистраль',
                'Обработка отмененного или невостребованного товара', 'Обработка возврата'],
        aggfunc='sum'
    )
    pivot_table_1['Итог'] = pivot_table_1['Количество'] + pivot_table_1['Обратная логистика'] + pivot_table_1['Обработка невыкупленного товара'] + pivot_table_1['Обработка возврата']
    # ToDatabase.store_data(pivot_table_1, f'wb_layuot_{name}')

    # Продажи (сумма в начислениях)
    filtered_df = df[(df['Тип начисления'] == 'Доставка покупателю')]
    pivot_table_2 = filtered_df.pivot_table(
        index='Код',
        values=['Итого', 'Ставка комиссии', 'Количество', 'За продажу или возврат до вычета комиссий и услуг'],
        aggfunc={'Итого': 'sum', 'Ставка комиссии': 'mean', 'Количество': 'sum', 'За продажу или возврат до вычета комиссий и услуг': 'sum'},
    )
    pivot_table_2['Итог'] = pivot_table_2['Ставка комиссии'] * pivot_table_2['За продажу или возврат до вычета комиссий и услуг']
    temp_data_2 = pivot_table_2['Итого'].sum() / 2
    pivot_table_2.columns = ['Итого', 'Ставка комиссии', 'Продажи, шт', 'За продажу или возврат до вычета комиссий и услуг']
    # ToDatabase.store_data(pivot_table_2, f'wb_layuot_Логистика без вычета сторно, возвраты /отказы')

    # Логистика
    # filtered_df = df[(df['Тип начисления'] == 'Доставка покупателю')]
    pivot_table_3 = filtered_df.pivot_table(
        index='Код',
        values=['Сборка заказа', 'Обработка отправления (Drop-off/Pick-up)', 'Магистраль', 'Последняя миля'],
        aggfunc='sum',
    )
    pivot_table_3['Итог'] = pivot_table_3['Сборка заказа'] + pivot_table_3['Обработка отправления (Drop-off/Pick-up)'] + pivot_table_3['Магистраль'] + pivot_table_3['Последняя миля']
    temp_data_3 = pivot_table_3['Итог'].sum()
    # ToDatabase.store_data(pivot_table_3, f'wb_layuot_{name}')

    # Реклама
    filtered_df = df[(df['Тип начисления'] == 'Услуги продвижения товаров')]
    pivot_table_4 = filtered_df.pivot_table(
        index='Название',
        values='Итого',
        aggfunc='sum'
    )
    temp_data_4 = pivot_table_4['Итого'].sum() / 2
    # ToDatabase.store_data(pivot_table_4, f'wb_layuot_Продажи')

    # Склад
    filtered_df = df[(df['Тип начисления'] == 'Услуга размещения товаров на складе')]
    pivot_table_5 = filtered_df.pivot_table(
        values='Итого',
        aggfunc='sum'
    )

    # Общий
    filtered_df = df[(df['Тип начисления'] == 'Доставка и обработка возврата, отмены, невыкупа') |
                     (df['Тип начисления'] == 'Доставка покупателю') |
                     (df['Тип начисления'] == 'Начисление за хранение/утилизацию возвратов') |
                     (df['Тип начисления'] == 'Оплата эквайринга') |
                     (df['Тип начисления'] == 'Получение возврата, отмены, невыкупа от покупателя')]
    pivot_table_6 = filtered_df.pivot_table(
        index='Код',
        values='Итого',
        aggfunc='sum'
    )
    pivot_table_6 = pd.concat([pivot_table_6, pivot_table_2['Количество']], axis=1)
    pivot_table_6 = pd.concat([pivot_table_6, df['Себестоимость']], axis=1)
    pivot_table_6['Общая себестоимость'] = pivot_table_6['Себестоимость'] * pivot_table_6['Количество']
    pivot_table_6['Прибыль'] = pivot_table_6['Итого'] - (pivot_table_6['Количество'] * pivot_table_6['Себестоимость'])
    pivot_table_6 = pd.concat([pivot_table_6, df['Группа']], axis=1)
    temp_data_6_store = pivot_table_5['Итого'].sum()
    temp_data_6_ad = temp_data_4
    temp_data_6_money = pivot_table_6['Прибыль'].sum()
    temp_data_6_store_2 = temp_data_6_money / (pivot_table_6['Итого'].sum() + temp_data_6_store)

    # Невыкуп - возврат
    filtered_df = df[(df['Тип начисления'] == 'Получение возврата, отмены, невыкупа от покупателя')]
    pivot_table_7 = filtered_df.pivot_table(
        index='Код',
        values=['Количество', 'Обратная логистика', 'Обработка невыкупленного товара', 'Обратная магистраль', 'Обработка отмененного или невостребованного товара', 'Обработка возврата'],
        aggfunc='sum'
    )
    pivot_table_7.columns = ['Возврат', 'Обратная логистика', 'Обработка невыкупленного товара',
                             'Обратная магистраль', 'Обработка отмененного или невостребованного товара', 'Обработка возврата']

    # Итог
    pivot_table_total = df.pivot_table(
        index=['Код'],
        values=['Итого', 'За продажу или возврат до вычета комиссий и услуг',
                'Закупочная цена', 'Цена товара'],
        aggfunc={'Итогр': 'sum',
                 'За продажу или возврат до вычета комиссий и услуг': 'sum',
                 'Закупочная цена': 'mean',
                 'Цена товара': 'max'
                 }
    )
    pivot_table_total = pd.concat([pivot_table_total, df['ИП']])
    pivot_table_total = pd.concat([pivot_table_total, pivot_table_2['Продажи, шт']])
    pivot_table_total = pivot_table_total['Продажи, шт'].fillna(0).astype(int)
    pivot_table_total = pd.concat([pivot_table_total, pivot_table_7['Возврат']])
    pivot_table_total = pivot_table_total['Возрат'].fillna(0).astype(int)
    pivot_table_total['Продажи-возвраты, шт'] = pivot_table_total['Продажи, шт'] - pivot_table_total['Возрат']
    pivot_table_total['Себестоимость'] = pivot_table_total['Закупочная цена'] * pivot_table_total['Продажи-возвраты, шт']
    pivot_table_total['Маржа'] = pivot_table_total['Итого'] - pivot_table_total['Себестоимость']
    pivot_table_total['Маржа (%)'] = pivot_table_total.apply(safe_division, axis=1)
    pivot_table_total['Стоимость товара'] = pivot_table_total['Продажи-возвраты, шт'] * pivot_table_total['Цена товара']
    pivot_table_total['Налог'] = pivot_table_total.apply(total_taxes)
    # ToDatabase.store_data(pivot_table_total, f'wb_layuot_Итого')

    a = int(input('Введите самовыкупы: '))
    b = a * 0.18 + (55+35+100) * a / 800
    c = int(input('Введите внешнюю рекламу: '))
    d = int(input('Введите доп. потери: '))
    names = ['Сумма', 'Доля']
    temp_total = pivot_table_total['За продажу или возврат до вычета комиссий и услуг'].sum()
    f = pivot_table_transf_5['Итого'].sum()
    data = {
        'Месяц': [month, month],
        'Неделя': [date, date],
        'Логистика': [pivot_table_transf['Логистика'].sum() - pivot_table_transf_1['За продажу или возврат до вычета комиссий и услуг'].sum(),
                      (pivot_table_transf['Логистика'].sum() - pivot_table_transf_1['За продажу или возврат до вычета комиссий и услуг'].sum()) / temp_total if temp_total != 0 else 0],
        'Комиссия': [(pivot_table_total['За продажу или возврат до вычета комиссий и услуг'].sum() - pivot_table_total['Итого'].sum()
                     - (pivot_table_transf['Логистика'].sum() - pivot_table_transf_1['За продажу или возврат до вычета комиссий и услуг'].sum())
                     - (a + d + f) - pivot_table_transf_2['Итого'].sum() - (pivot_table_transf_3['Итого'].sum() - pivot_table_transf_4['Итого'].sum())),
                     ((pivot_table_total['За продажу или возврат до вычета комиссий и услуг'].sum() - pivot_table_total['Итого'].sum()
                     - (pivot_table_transf['Логистика'].sum() - pivot_table_transf_1['За продажу или возврат до вычета комиссий и услуг'].sum())
                     - (a + d + f) - pivot_table_transf_2['Итого'].sum() - (pivot_table_transf_3['Итого'].sum() - pivot_table_transf_4['Итого'].sum()))
                     / temp_total if temp_total != 0 else 0)],
        'Склад+ЗП': [pivot_table_total['Себестоимость'].sum() - pivot_table_total['Стоимость товара'].sum() - pivot_table_total['Налог'].sum(),
                     pivot_table_total['Себестоимость'].sum() - pivot_table_total['Стоимость товара'].sum() -
                     pivot_table_total['Налог'].sum() / temp_total if temp_total != 0 else 0],
        'Товар': [pivot_table_total['Стоимость товара'].sum(),
                  pivot_table_total['Стоимость товара'].sum() / temp_total if temp_total != 0 else 0],
        'Маржа': [pivot_table_total['Маржа'].sum() - (a + b + c + d), pivot_table_total['Маржа'].sum() - (a + b + c + d) / temp_total if temp_total != 0 else 0],
        'Продвижение': [a + d + f, (a + d + f) / temp_total if temp_total != 0 else 0],
        'Хранение': [pivot_table_transf_2['Итого'].sum(), pivot_table_transf_2['Итого'].sum() / temp_total if temp_total != 0 else 0],
        'Штрафы': [pivot_table_transf_3['Итого'].sum() - pivot_table_transf_4['Итого'].sum(), (pivot_table_transf_3['Итого'].sum() - pivot_table_transf_4['Итого'].sum()) / temp_total if temp_total != 0 else 0],
        'Налоги': [pivot_table_total['Налог'].sum(), pivot_table_total['Налог'].sum() / temp_total if temp_total != 0 else 0]
    }

    df_result = pd.DataFrame(data=data, index=names)
    return df_result
