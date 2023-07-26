import pandas as pd
import ast
import re

pd.options.mode.chained_assignment = None


def format_report(data):
    print("Приводит полученный json-файл в формат таблицы...")
    df = pd.DataFrame(pd.json_normalize(data['rows'], errors='ignore'))

    headers_to_remove = ['updated', 'archived', 'effectiveVat', 'effectiveVatEnabled', 'vat', 'vatEnabled',
                         'useParentVat',
                         'meta.href', 'meta.href', 'meta.uuidHref', 'meta.mediaType', 'owner.meta.href',
                         'owner.meta.metadataHref', 'owner.meta.type', 'owner.meta.mediaType', 'owner.meta.uuidHref',
                         'group.meta.href', 'group.meta.metadataHref', 'group.meta.metadataHref', 'group.meta.type',
                         'group.meta.mediaType', 'productFolder.meta.href', 'productFolder.meta.metadataHref',
                         'productFolder.meta.type', 'productFolder.meta.mediaType', 'productFolder.meta.uuidHref',
                         'uom.meta.href', 'uom.meta.metadataHref', 'uom.meta.type', 'uom.meta.mediaType',
                         'images.meta.href', 'images.meta.type', 'images.meta.mediaType', 'images.meta.size',
                         'images.meta.limit', 'images.meta.offset', 'minPrice.currency.meta.href',
                         'minPrice.currency.meta.metadataHref', 'minPrice.currency.meta.type',
                         'minPrice.currency.meta.mediaType', 'minPrice.currency.meta.uuidHref',
                         'buyPrice.currency.meta.href', 'buyPrice.currency.meta.metadataHref',
                         'buyPrice.currency.meta.type', 'buyPrice.currency.meta.mediaType',
                         'buyPrice.currency.meta.uuidHref', 'files.meta.href', 'files.meta.type',
                         'files.meta.mediaType',
                         'files.meta.size', 'files.meta.limit', 'files.meta.offset', 'id', 'accountId', 'shared',
                         'externalCode', 'paymentItemType', 'discountProhibited', 'volume', 'variantsCount',
                         'isSerialTrackable', 'trackingType', 'tnved', 'partialDisposal', 'meta.metadataHref',
                         'meta.type',
                         'minPrice.value']
    df = df.drop(columns=headers_to_remove, axis=1)

    # Баркоды
    df['barcodes'] = df['barcodes'].astype(str).str[1:-1]
    df[['ean13', 'ean8']] = (df['barcodes'].astype(str)).str.split(', ', 1, expand=True)
    for index, value in df['ean8'].iteritems():
        x = str(value)
        match1 = re.search(r"'ean8': '([^']+)'", x)
        match2 = re.search(r"'ean13': '([^']+)'", x)
        if match1:
            df['ean8'][index] = match1.group(1)
        elif match2:
            if re.search(r" 'ean8': '([^']+)'", str(df['ean13'][index])):
                df['ean8'][index] = re.search(r" 'ean8': '([^']+)'", str(df['ean13'][index])).group(1)
                df['ean13'][index] = match2.group(1)
            else:
                df['ean13'][index] = match2.group(1)
        elif value == "{'ean8': 'нет'}, {'ean8': 'кт'}":
            df['ean8'][index] = "нет КТ"
        elif value is None:
            df['ean8'][index] = ""
        else:
            df['ean8'][index] = f"Некорректные данные: + {value}"
    for index, value in df['ean13'].iteritems():
        x = str(value)
        match1 = re.search(r"'ean13': '([^']+)'", x)
        match2 = re.search(r"'ean8': '([^']+)'", x)
        if match1:
            df['ean13'][index] = match1.group(1)
        elif match2:
            if re.search(r" 'ean13': '([^']+)'", str(df['ean8'][index])):
                df['ean13'][index] = re.search(r" 'ean13': '([^']+)'", str(df['ean8'][index])).group(1)
                df['ean8'][index] = match2.group(1)
            else:
                df['ean8'][index] = match2.group(1)
            df['ean8'][index] = match2.group(1)
        elif value == "{'ean`13`': 'нет'}, {'ean13': 'кт'}":
            df['ean13'][index] = "нет КТ"
        else:
            df['ean13'][index] = f"Некорректные данные: + {value}"
    df = df.drop(columns=['barcodes'], axis=1)

    # Атрибуты
    df['attributes'] = ((df['attributes'].astype(str)).str[1:-1])
    df[['Артикул на сайте WB', 'ABC анализ', 'Логистика (Кит-Мск)']] = pd.DataFrame([['', '', '']], index=df.index)
    for index, value in df['attributes'].iteritems():
        js_attributes = pd.json_normalize(ast.literal_eval(value))
        for i in range(0, 18):
            try:
                if (js_attributes['name'][i]) == 'Артикул на сайте WB':
                    df['Артикул на сайте WB'][index] = js_attributes['value'][i]
                elif (js_attributes['name'][i]) == 'ABC анализ':
                    df['ABC анализ'][index] = js_attributes['value'][i]
                elif (js_attributes['name'][i]) == 'Логистика (Кит-Мск)':
                    df['Логистика (Кит-Мск)'][index] = js_attributes['value'][i]
            except KeyError:
                break
    df = df.drop(columns=['attributes'], axis=1)

    # Артикул без '/'
    df['Артикул (убрали все после /)'] = df['article'].str.split('/').str[0]

    # SalesPrices
    df['salePrices'] = (df['salePrices'].astype(str)).str[1:-1]
    df['Цена закупки в Юанях'] = ''
    for index, value in df['salePrices'].iteritems():
        js_sales = pd.json_normalize(ast.literal_eval(value))
        for i in range(0, 5):
            if (js_sales['priceType.name'][i]) == 'Цена закупки в юанях':
                df['Цена закупки в Юанях'][index] = js_sales['value'][i]
    df = df.drop(columns=['salePrices'], axis=1)

    # Приведение столбцов
    df['buyPrice.value'] = df['buyPrice.value'].astype(float) / 100
    df['buyPrice.value'] = df['buyPrice.value'].astype(str)
    df['buyPrice.value'] = df['buyPrice.value'].str.replace(".", ",", regex=True)
    df['Цена закупки в Юанях'] = df['Цена закупки в Юанях'].astype(float) / 100
    df['Цена закупки в Юанях'] = df['Цена закупки в Юанях'].astype(str)
    df['Цена закупки в Юанях'] = df['Цена закупки в Юанях'].str.replace(".", ",", regex=True)
    df['Логистика (Кит-Мск)'] = df['Логистика (Кит-Мск)'].astype(str)
    df['Логистика (Кит-Мск)'] = df['Логистика (Кит-Мск)'].str.replace(".", ",", regex=True)
    df['weight'] = df['weight'].astype(str)
    df['weight'] = df['weight'].str.replace('.', ',', regex=True)

    df['Пусто'] = ''
    df = df[
        ['code', 'article', 'Артикул (убрали все после /)', 'Артикул на сайте WB', 'ean13', 'pathName', 'code', 'name',
         'article', 'Цена закупки в Юанях', 'buyPrice.value', 'ean13', 'ean8', 'weight', 'Артикул на сайте WB',
         'ABC анализ', 'Логистика (Кит-Мск)', 'Пусто', 'minimumBalance', 'Пусто']]

    df.columns = ['Код', 'Артикул (с /)', 'Артикул', 'Доп. поле: Артикул на сайте WB', 'Штрихкод EAN13',
                  'Группы', 'Код_1', 'Наименование', 'Артикул_2', 'Цена: Цена закупки в юанях', 'Закупочная цена',
                  'Штрихкод EAN13_3', 'Штрихкод EAN8', 'Вес', 'Доп. поле: Артикул на сайте WB_4', 'Доп. поле: ABC анализ',
                  'Доп. поле: Логистика (Кит-Мск)', 'Доп. поле: Дата поступления первого остатка', 'Остаток',
                  'Продаж в день']

    return df


def check(data):
    if (data.count()[0] % 1000) == 0:
        return True
    else:
        return False


def format_cvs(df_to_cvs):
    csv_path = 'reports/temp/MyStore.csv'
    df_to_cvs.to_csv(csv_path, header=True, index=False)
