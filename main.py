# Сбор и разметка данных (семинары)
# Урок 4. Парсинг HTML. XPath

# Задание
# 1. Выберите веб-сайт с табличными данными, который вас интересует.
# 2. Напишите код Python, использующий библиотеку requests для отправки HTTP GET-запроса
#    на сайт и получения HTML-содержимого страницы.
# 3. Выполните парсинг содержимого HTML с помощью библиотеки lxml, чтобы извлечь данные из таблицы.
# 4. Сохраните извлеченные данные в CSV-файл с помощью модуля csv.
#
# Ваш код должен включать следующее:
#
# - Строку агента пользователя в заголовке HTTP-запроса, чтобы имитировать веб-браузер и избежать
#   блокировки сервером.
# - Выражения XPath для выбора элементов данных таблицы и извлечения их содержимого.
# - Обработка ошибок для случаев, когда данные не имеют ожидаемого формата.
# - Комментарии для объяснения цели и логики кода.
#
# Примечание: Пожалуйста, не забывайте соблюдать этические и юридические нормы при веб-скреппинге.

import requests
from lxml import html
import csv
import re
from tqdm import tqdm
from time import sleep

TARGET_URL = 'https://jofel.ru/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
DELAY = 0.1
RESULT_FILE = 'rezult.csv'


def get_categories(local_url):
    """
    Генерируем список ссылок на категории товаров сайта, указанного в local_url
    :param local_url: Адрес сайта
    :return: Список ссылок на категории товаров
    """
    response = requests.get(local_url, headers=HEADERS)
    tree = html.fromstring(response.content)
    categories_url = tree.xpath('//div[@class="__content"]/h3/a/@href')
    sleep(DELAY)
    return [TARGET_URL + local_category[1:] for local_category in categories_url
            if local_category not in ('/catalog/aktsii_catalog/', '/catalog/novinki_catalog/')]  # Выкидываем эти две,
    # т.к. тут товары повторяются


def get_pages(category_url):
    """
    Генерируем список ссылок на страницы с товарами в указанной категории
    :param category_url: Ссылка на категорию
    :return: Список ссылок на товары
    """
    ret = []
    current_url = category_url
    while current_url:  # Страница с товарами может быть не одна
        response = requests.get(current_url, headers=HEADERS)
        tree = html.fromstring(response.content)
        try:
            items_table = tree.xpath("//a[@class='__full-link']/@href")
            for item in items_table:
                ret.append(TARGET_URL + item[1:])  # Сслыка на товар
        except (Exception,):
            pass
        try:
            next_page = tree.xpath("//a[@class='fontello-angle-double-right']/@href")  # Проверка на следующую страницу
            if next_page:
                current_url = TARGET_URL + next_page[0][1:]
            else:
                current_url = None
        except (Exception,):
            current_url = None
        sleep(DELAY)
    return ret


def get_data(local_page):
    """
    Парсим данные с указанной страницы
    :param local_page: Адрес страницы
    :return: Словарь с данными со страницы
    """
    page_data = {  # Заполняем структуру, чтобы она сохранялась, если вдруг данные будут неполными
        'Category': None,
        'Name': None,
        'VendorCode': None,
        'Vendor': None,
        'Price_Eur': None,
        'Price_Rub': None,
        'Product_url': local_page,
        'Image_url': None,
    }
    response = requests.get(local_page, headers=HEADERS)
    tree = html.fromstring(response.content)
    try:
        page_data['Category'] = tree.xpath("//ul[@class='breadcrumbs']/li/a/text()")[2]
    except (Exception,):
        pass
    try:
        page_data['Name'] = tree.xpath("//h1[@class='__title h2']/text()")[0]
    except (Exception,):
        pass
    try:
        page_data['Image_url'] = TARGET_URL + tree.xpath("//figure[@class='__image __image--big']/a/@href")[0][1:]
    except (Exception,):
        pass
    try:
        characteristics = tree.xpath("//div[@class='__line __line--info']/p/b/text()")
        page_data['VendorCode'] = characteristics[0]
        page_data['Vendor'] = characteristics[1]
    except (Exception,):
        pass
    try:
        page_data['Price_Eur'] = float("".join(re.findall('[0-9.,]',
                                                          tree.xpath("//div[@class='__line __line--price']/p/text()")[
                                                              0])).
                                       replace(',', '.'))
    except ValueError:
        pass
    try:
        page_data['Price_Rub'] = float("".join(re.findall('[0-9.,]',
                                                          tree.xpath("//div[@class='__line __line--price']/p/text()")[
                                                              1])).
                                       replace(',', '.'))
    except ValueError:
        pass
    sleep(DELAY)
    return page_data


def my_save_to_csv(filename, local_data):
    """
    Записываем список из словарей local_data в CSV-файл filename
    :param filename: Путь к файлу для записи
    :param local_data: Список из словарей с данными
    :return:
    """
    with open(filename, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Category', 'Name', 'VendorCode', 'Vendor', 'Series',  # Пишем заголовок
                         'Price_Eur', 'Price_Rub', 'Product_url', 'Image_url'])
        for row in local_data:
            writer.writerow(row.values())


if __name__ == '__main__':
    categories = get_categories(TARGET_URL + '/catalog/')

    pages = []
    for category in tqdm(categories, '(1/2) Категории'):
        pages.extend(get_pages(category))

    data = [get_data(page) for page in tqdm(pages, '(2/2) Страницы')]

    my_save_to_csv(RESULT_FILE, data)
    print(f'Данные сохранены в файле {RESULT_FILE}')

# Результат работы:
# /home/user/Work/Python/Data/PyData_dz4/.venv/bin/python /home/user/Work/Python/Data/PyData_dz4/main.py
# (1/2) Категории: 100%|██████████| 12/12 [00:11<00:00,  1.01it/s]
# (2/2) Страницы: 100%|██████████| 174/174 [01:56<00:00,  1.49it/s]
# Данные сохранены в файле rezult.csv
#
# Process finished with exit code 0
