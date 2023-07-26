import pandas as pd
from API import GetReports
import ast


def format_report(data, period):
    print("Приводит полученный json-файл в формат таблицы...")
    df = pd.DataFrame(pd.json_normalize(data['result']['operations'], errors='ignore'))
    df['Период'] = str(period)
    df['ИП'] = "Эккель"

    # Services
    df['services'] = ((df['services'].astype(str)).str[1:-1])
    df[['Логистика', 'Обратная логистика']] = pd.DataFrame([[0, 0]], index=df.index)
    df[['Ставка комиссии', 'Комиссия за продажу', 'Итого', 'Сборка заказа', 'Обработка отправления (Drop-off/Pick-up)',
        'Обработка невыкупа', 'Обработка возврата невостребованного товара', 'Магистраль', 'Обратная магистраль',
        'Последняя миля', 'Обработка отмен']] = pd.DataFrame([['', 0.00, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
                                                             index=df.index)
    for index, value in df['services'].iteritems():
        try:
            js_services = pd.json_normalize(ast.literal_eval(value))
            for i in range(0, 13):
                try:
                    if js_services['name'][i] == 'MarketplaceServiceItemFulfillment':
                        df['Сборка заказа'][index] = js_services['price'][i]
                    elif js_services['name'][i] is ['MarketplaceServiceItemDropoffFF',
                                                    'MarketplaceServiceItemDropoffPVZ',
                                                    'MarketplaceServiceItemDropoffSC',
                                                    'MarketplaceServiceItemPickup ']:
                        df['Обработка отправления (Drop-off/Pick-up)'][index] = js_services['price'][i]
                    elif js_services['name'][i] == 'MarketplaceServiceItemReturnPartGoodsCustomer':
                        df['Обработка невыкупа'][index] = js_services['price'][i]
                    elif js_services['name'][i] == 'MarketplaceServiceItemReturnNotDelivToCustomer':
                        df['Обработка отмен'][index] = js_services['price'][i]
                    elif js_services['name'][i] == 'MarketplaceServiceItemReturnAfterDelivToCustomer':
                        df['Обработка возврата невостребованного товара'][index] = js_services['price'][i]
                    elif js_services['name'][i] == 'MarketplaceNotDeliveredCostItem':
                        df['Обработка возврата невостребованного товара'][index] += js_services['price'][i]
                    elif js_services['name'][i] == 'MarketplaceServiceItemDirectFlowTrans':
                        df['Магистраль'][index] = js_services['price'][i]
                    elif js_services['name'][i] == 'MarketplaceServiceItemReturnFlowTrans':
                        df['Обратная магистраль'][index] = js_services['price'][i]
                    elif js_services['name'][i] == 'MarketplaceServiceItemDelivToCustomer':
                        df['Последняя миля'][index] = js_services['price'][i]
                    elif js_services['name'][i] == 'MarketplaceServiceItemDirectFlowLogistic':
                        df['Логистика'][index] = js_services['price'][i]
                    elif js_services['name'][i] == 'MarketplaceServiceItemReturnFlowLogistic':
                        df['Обратная логистика'][index] = js_services['price'][i]
                except KeyError:
                    break
        except SyntaxError:
            continue

    # Items
    df['items'] = ((df['items'].astype(str)).str[1:-1])
    df[['SKU', 'Наименование', 'Количество']] = pd.DataFrame(
        [['', '', '']], index=df.index)
    for index, value in df['items'].iteritems():
        try:
            js_items = pd.json_normalize(ast.literal_eval(value))
            df['Количество'][index] = len(js_items)
            df['SKU'][index] = js_items['sku'][0]
            df['Наименование'][index] = js_items['name'][0]
        except SyntaxError:
            continue

    # Артикулы
    df_article = GetReports.get_article_ozon(df['SKU'].values.tolist())
    df = pd.merge(df, df_article, on='SKU', how='left')

    # Услуги
    # for index, value in df['services'].iteritems():

    # Ставка комиссии
    df['Ставка комиссии'] = 0.0
    for index, value in df['accruals_for_sale'].iteritems():
        try:
            df['Ставка комиссии'][index] = int(value) / int(df['sale_commission'][index])
        except (ZeroDivisionError, ValueError):
            df['Ставка комиссии'][index] = 0.0

    df = df[
        ['Период', 'ИП', 'operation_date', 'operation_type_name', 'posting.posting_number', 'posting.order_date',
         'posting.delivery_schema', 'SKU', 'Артикул', 'Наименование', 'Количество',
         'accruals_for_sale', 'Ставка комиссии', 'sale_commission', 'Сборка заказа',
         'Обработка отправления (Drop-off/Pick-up)', 'Магистраль', 'Последняя миля', 'Обратная магистраль',
         'Обработка возврата невостребованного товара', 'Обработка отмен', 'Обработка невыкупа', 'Логистика',
         'Обратная логистика', 'amount']]

    df.columns = ['Период', 'ИП', 'Дата начисления', 'Тип начисления', 'Номер отправления',
                  'Дата принятия заказа в обработку', 'Склад отгрузки', 'SKU', 'Артикул', 'Название', 'Количество',
                  'За продажу или возврат до вычета комиссий и услуг', 'Ставка комиссии', 'Комиссия за продажу',
                  'Сборка заказа', 'Обработка отправления (Drop-off/Pick-up)', 'Магистраль', 'Последняя миля',
                  'Обратная магистраль', 'Обработка возврата', 'Обработка отмененного или невостребованного товара',
                  'Обработка невыкупленного товара', 'Логистика', 'Обратная логистика', 'Итого']

    df['За продажу или возврат до вычета комиссий и услуг'] = (
        df['За продажу или возврат до вычета комиссий и услуг'].astype(str)).str.replace(".", ",", regex=True)
    df['Ставка комиссии'] = (
        (df['Ставка комиссии'].astype(float) / 100).astype(str)).str.replace(".", ",", regex=True)
    df['Комиссия за продажу'] = (
        df['Комиссия за продажу'].astype(str)).str.replace(".", ",", regex=True)
    df['Сборка заказа'] = (
        df['Сборка заказа'].astype(str)).str.replace(".", ",", regex=True)
    df['Обработка отправления (Drop-off/Pick-up)'] = (
        df['Обработка отправления (Drop-off/Pick-up)'].astype(str)).str.replace(".", ",", regex=True)
    df['Магистраль'] = (
        df['Магистраль'].astype(str)).str.replace(".", ",", regex=True)
    df['Последняя миля'] = (
        df['Последняя миля'].astype(str)).str.replace(".", ",", regex=True)
    df['Обратная магистраль'] = (
        df['Обратная магистраль'].astype(str)).str.replace(".", ",", regex=True)
    df['Обработка возврата'] = (
        df['Обработка возврата'].astype(str)).str.replace(".", ",", regex=True)
    df['Обработка отмененного или невостребованного товара'] = (
        df['Обработка отмененного или невостребованного товара'].astype(str)).str.replace(".", ",", regex=True)
    df['Обработка невыкупленного товара'] = (
        df['Обработка невыкупленного товара'].astype(str)).str.replace(".", ",", regex=True)
    df['Логистика'] = (
        df['Логистика'].astype(str)).str.replace(".", ",", regex=True)
    df['Обратная логистика'] = (
        df['Обратная логистика'].astype(str)).str.replace(".", ",", regex=True)
    df['Итого'] = (
        df['Итого'].astype(str)).str.replace(".", ",", regex=True)

    return df


def format_article(data):
    try:
        df = pd.DataFrame(pd.json_normalize(data['result']['items'], errors='ignore'))
        df = df[['fbo_sku', 'offer_id']]
        df.columns = ['SKU', 'Артикул']
    except KeyError:
        df = pd.DataFrame([['', '']], columns=['SKU', 'Артикул'])
    return df


def check(data):
    if (data.count()[0] % 1000) == 0:
        return True
    else:
        return False


def format_cvs(df_to_cvs):
    csv_path = 'reports/temp/Ozon.csv'
    df_to_cvs.to_csv(csv_path, header=True, index=False, encoding='utf-8')
