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

target_url = 'https://jofel.ru/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
DELAY = 0.1

def get_categories(local_url):
    response = requests.get(local_url, headers=HEADERS)
    tree = html.fromstring(response.content)
    categories_table = tree.xpath('/html/body/main/section[2]/div/div/div/div/div')
    categories_url = categories_table[0].xpath('.//h3/a/@href')
    return [target_url + category for category in categories_url
            if category not in ('/catalog/aktsii_catalog/','/catalog/novinki_catalog/')]

def get_pages(category_url):
    ret = []
    current_url = category_url
    response = requests.get(current_url,headers=HEADERS)
    tree = html.fromstring(response.content)
    items_table = tree.xpath("//form")
    table2 = items_table[0].xpath("//div[contains(@class, '__inner')]")

    #    items_table = tree.xpath("//div[contains(@class, '__inner')]")

    print(table2)
    # custom-btn custom-btn--style-1
#    items_url = items_table[2].xpath("//a/text()")
    #
#    print(items_url)

    return ret

if __name__ == '__main__':

    categories = get_categories(target_url + '/catalog/')
    pages = [get_pages(page) for page in categories[:1]]
#    print(pages)

