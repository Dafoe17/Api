import pandas as pd


def format_report(data, wb_id):
    print("Приводит полученный json-файл в формат таблицы...")
    df = pd.DataFrame(pd.json_normalize(data, errors='ignore'))
    df['ИП'] = wb_id
    print('Форматируем таблицу...')
    # Загрузка таблицы из файла
    headers_to_remove = {'create_dt', 'suppliercontract_code'}
    for header in headers_to_remove:
        df = df.drop(header, axis=1)

    df['date_from'] = pd.to_datetime(df['date_from'], format="%d.%m.%Y", infer_datetime_format=True, utc=True,
                                     errors='ignore').dt.date
    df['date_to'] = pd.to_datetime(df['date_to'], format="%d.%m.%Y", infer_datetime_format=True, utc=True,
                                   errors='ignore').dt.date
    df['order_dt'] = pd.to_datetime(df['order_dt'], format="%d.%m.%Y", infer_datetime_format=True, utc=True,
                                    errors='ignore').dt.date
    df['sale_dt'] = pd.to_datetime(df['sale_dt'], format="%d.%m.%Y", infer_datetime_format=True, utc=True,
                                   errors='ignore').dt.date

    df['Период'] = df['date_from'].astype(str) + ' — ' + df['date_to'].astype(str)

    df['all_sale_percent'] = df['sale_percent']  # Спросить как вычисляется Итоговая согласованная скидка

    df = df[
        ["realizationreport_id", "ИП", "Период", "rrd_id", "gi_id", "subject_name", "nm_id", "brand_name", "sa_name",
         "ts_name", "barcode", "doc_type_name", "supplier_oper_name", "order_dt", "sale_dt", "quantity", "retail_price",
         "retail_amount", "sale_percent", "supplier_promo", "all_sale_percent", "retail_price_withdisc_rub",
         "sup_rating_prc_up", "is_kgvp_v2", "ppvz_spp_prc", "commission_percent", "ppvz_kvw_prc_base", "ppvz_kvw_prc",
         "ppvz_sales_commission", "ppvz_reward", "acquiring_fee", "ppvz_vw", "ppvz_vw_nds", "ppvz_for_pay",
         "delivery_amount", "return_amount", "delivery_rub", "penalty", "additional_payment", "bonus_type_name",
         "sticker_id", "acquiring_bank", "ppvz_office_id", "ppvz_office_name", "ppvz_inn", "ppvz_supplier_name",
         "office_name", "site_country", "gi_box_type_name", "declaration_number", "shk_id", "rid", "srid",
         "rebill_logistic_cost", "rebill_logistic_org"]]

    df.columns = ["Отчет", "ИП", "Период", "№", "Номер поставки", "Предмет", "Код номенклатуры", "Бренд",
                  "Артикул", "Размер", "Баркод", "Тип Документа", "Обоснования для оплаты",
                  "Дата заказа покупателем", "Дата продажи", "Кол-во", "Цена розничная",
                  "Вайлдберриз реализовал Товар (Пр)", "Согласованный продуктовый дисконт, %", "Промокод %",
                  "Итоговая согласованная скидка", "Цена розничная с учетом согласованной скидки",
                  "Размер снижения кВВ из-за рейтинга, %", "Размер снижения кВВ из-за акции, %",
                  "Скидка постоянного Покупателя (СПП)", "Размер кВВ, %", "Размер  кВВ без НДС, % Базовый",
                  "Итоговый кВВ без НДС, %", "Вознаграждение с продаж до вычета услуг поверенного, без НДС",
                  "Возмещение за выдачу и возврат товаров на ПВЗ", "Возмещение издержек по эквайрингу",
                  "Вознаграждение Вайлдберриз (ВВ), без НДС", "НДС с Вознаграждения Вайлдберриз",
                  "К перечислению Продавцу за реализованный Товар", "Количество доставок", "Количество возврата",
                  "Услуги по доставке товара покупателю", "Общая сумма штрафов", "Доплаты",
                  "Виды логистики, штрафов и доплат", "Стикер МП", "Наименование банка-эквайера", "Номер офиса",
                  "Наименование офиса доставки", "ИНН партнера", "Партнер", "Склад", "Страна", "Тип коробов",
                  "Номер таможенной декларации", "ШК", "Rid", "Srid", "Возмещение издержек по перевозке",
                  "Организатор перевозки"]

    for i in range(17, 39):
        df.iloc[:, i] = df.iloc[:, i].astype(str)
        df.iloc[:, i] = df.iloc[:, i].str.replace(".", ",", regex=True)

    csv_path = 'reports/temp/Wb.csv'
    df.to_csv(csv_path, header=True, index=False)

    period_array = df['Период'].unique()

    return df, period_array
