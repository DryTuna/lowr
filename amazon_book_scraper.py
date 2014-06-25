import requests
from bs4 import BeautifulSoup
from P_Queue import P_Queue


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_search_results(keywords="",
                         rh='n:283155',
                         page=None,
                         min_p=None,
                         price_range=20):
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
        print "hi"
    if min_p is not None:
        params['low-price'] = min_p - (min_p * price_range / 100)
        params['high-price'] = min_p + (min_p * price_range / 100)
    resp = requests.get(base, params=params, timeout=3)
    resp.raise_for_status()
    return resp.content, resp.encoding


def extract_items(parsed, min_p, max_p):
    books = parsed.find_all('div', class_='result')
    print len(books)
    for book in books:
        img = book.find('div', class_='imageBox').find('img')
        link = book.find('div', class_='data').find('a')
        prime_price = book.find('td', class_= 'toeOurPrice')
        new_price = book.find('td', class_='toeNewPrice')
        item = item_dictionary(img, link, prime_price, new_price, min_p, max_p)
        if item is not None:
            yield item


def item_dictionary(img, link, prime_price, new_price, min_p=None, max_p=None):
    item = {}
    item['image'] = img.attrs['src']
    item['link'] = link.attrs['href']
    item['title'] = link.string.strip()
    item['prime_price'] = u'n/a'
    item['new_price'] = u'n/a'
    if "<a " in str(prime_price):
        prime_price = prime_price.find('a')
        item['prime_price'] = prime_price.string.strip()
    if "<a " in str(new_price):
        new_price = new_price.find('a')
        np = str(new_price.string.strip())[1:-3].replace(',', '')
        if min_p is not None:
            if int(np) >= min_p and int(np) <= max_p:
                item['new_price'] = new_price.string.strip()
                return item
        else:
            item['new_price'] = new_price.string.strip()
    return None if item['prime_price'] == u'n/a' else item


def search_results(keywords, category, price, price_range):
    count = 1
    page = 1
    min_p = None
    max_p = None
    price = int(price)
    price_range = int(price_range)
    if price is not None:
        min_p = price - (price * price_range / 100)
        max_p = price + (price * price_range / 100)
    p_queue = P_Queue()
    while count < 20:
        content = fetch_search_results(keywords,
                                       category,
                                       page,
                                       price,
                                       price_range)
        parsed = parse_source(content[0], content[1])
        if len(parsed.find_all('div', class_='result')) == 0:
            break
        items = extract_items(parsed, min_p, max_p)
        for i in items:
            pri = 0
            if i['prime_price'] == u'n/a':
                pri = int(i['new_price'][1:-3])
            else:
                pri = int(i['prime_price'][1:-3])
            p_queue.insert(i, pri)
            count += 1
        page += 1
    return p_queue


if __name__ == '__main__':
    a = search_results("To Kill a Mocking Bird", 'n:283155', 10, 100)
    f = open('extract.txt', 'w')
    while True:
        try:
            i = a.pop()
            f.write(str(i._priority) + "\t" + str(i._data) + "\n")
        except IndexError:
            break
    f.close()
