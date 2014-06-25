import requests
from bs4 import BeautifulSoup
from P_Queue import P_Queue


MIN_P = 1.0
MAX_P = 5000.0


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_search_results(keywords="",
                         rh='n:283155',
                         page=None):
    base = 'http://www.amazon.com/s/'
    if len(keywords) == 0:
        raise ValueError("Please enter search keys")
    params = {
        'ref': 'sr_st_relevancerank',
        'keywords': keywords,
        'rh': rh
    }
    if page is not None:
        params['page'] = page
    params['low-price'] = MIN_P
    params['high-price'] = MAX_P
    resp = requests.get(base, params=params, timeout=3)
    resp.raise_for_status()
    return resp.content, resp.encoding


def extract_items(parsed):
    books = parsed.find_all('div', class_='result')
    for book in books:
        img = book.find('div', class_='imageBox').find('img')
        link = book.find('div', class_='data').find('a')
        prime_price = book.find('td', class_= 'toeOurPrice')
        new_price = book.find('td', class_='toeNewPrice')
        item = item_dictionary(img, link, prime_price, new_price)
        if item is not None:
            yield item


def get_price(price_string):
    if price_string is not None:
        if '<a ' in str(price_string):
            x = price_string.find('a').string.strip()
            temp = str(x)[1:-3].replace(',', '')
            if int(temp) >= MIN_P and int(temp) <= MAX_P:
                return x
    return None


def item_dictionary(img, link, prime_price, new_price):
    item = {}
    item['image'] = img.attrs['src']
    item['link'] = link.attrs['href']
    item['title'] = link.string.strip()
    item['prime_price'] = get_price(prime_price)
    item['new_price'] = get_price(new_price)
    if item['prime_price'] is None:
        item['prime_price'] = u'n/a'
    if item['new_price'] is None:
        item['new_price'] = u'n/a'
    return item if item['new_price'] != 'n/a' \
        or item['prime_price'] != 'n/a' \
        else None


def search_results(keywords, category, price, price_range):
    count = 1
    page = 1
    if len(str(price)) > 0:
        price = float(price)
        price_range = float(price_range)
        global MIN_P
        MIN_P = price - (price * price_range / 100)
        global MAX_P
        MAX_P = price + (price * price_range / 100)
    p_queue = P_Queue()
    while count < 15:
        content = fetch_search_results(keywords,
                                       category,
                                       page)
        parsed = parse_source(content[0], content[1])
        if len(parsed.find_all('div', class_='result')) == 0:
            break
        items = extract_items(parsed)
        for i in items:
            pri = 0
            if i['prime_price'] == u'n/a':
                pri = int(i['new_price'][1:-3].replace(',', ''))
            else:
                pri = int(i['prime_price'][1:-3].replace(',', ''))
            p_queue.insert(i, pri)
            count += 1
        page += 1
    MIN_P = 1.0
    MAX_P = 5000.0
    return p_queue


if __name__ == '__main__':
    a = search_results("To Kill a Mocking Bird", 'n:283155', 10, 50)
    f = open('extract.txt', 'w')
    while True:
        try:
            i = a.pop()
            f.write(str(i._priority) + "\t" + str(i._data) + "\n")
        except IndexError:
            break
    f.close()
