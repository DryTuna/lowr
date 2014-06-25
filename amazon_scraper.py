import requests
from bs4 import BeautifulSoup
from P_Queue import P_Queue


MIN_P = 0
MAX_P = 5000


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_search_results(keywords="",
                         rh='i:aps',
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
    fst = parsed.find_all('div', class_='fstGrid prod celwidget')
    rslt = parsed.find_all('div', class_='rsltGrid prod celwidget')
    for block in fst:
        img = block.find('div', class_='imageBox').find('img')
        link = block.find('h3', class_='newaps').find('a')
        prime_price = block.find('span', class_='bld lrg red')
        new_price = block.find('span', class_='price bld')
        item = item_dictionary(img, link, prime_price, new_price)
        if item is not None:
            yield item
    for block in rslt:
        img = block.find('div', class_='imageBox').find('img')
        link = block.find('h3', class_='newaps').find('a')
        prime_price = block.find('span', class_='bld lrg red')
        new_price = block.find('span', class_='price bld')
        item = item_dictionary(img, link, prime_price, new_price)
        if item is not None:
            yield item


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


def get_price(price_string):
    if price_string is not None:
        x = price_string.string.strip()
        if '$' in x:
            temp = str(x)[1:-3].replace(',', '')
            if int(temp) >= MIN_P and int(temp) <= MAX_P:
                return x
    return None


def search_results(keywords, category, price, price_range):
    count = 1
    page = 1
    if price is not None:
        price = float(price)
        price_range = float(price_range)
        global MIN_P
        MIN_P = price - (price * price_range / 100)
        global MAX_P
        MAX_P = price + (price * price_range / 100)
    p_queue = P_Queue()
    while count < 10:
        content = fetch_search_results(keywords,
                                       category,
                                       page)
        parsed = parse_source(content[0], content[1])
        print "\nSEARCH RESULTS:\t"+str(len(parsed))+"\n"
        if len(parsed.find_all('div', class_='rsltGrid prod celwidget')) == 0:
            break
        items = extract_items(parsed)
        for i in items:
            pri = 0
            if i['prime_price'] == u'n/a':
                pri = int(i['new_price'][1:-3])
            else:
                pri = int(i['prime_price'][1:-3])
            p_queue.insert(i, pri)
            count += 1
        page += 1
    MIN_P = 0
    MAX_P = 5000
    return p_queue


if __name__ == '__main__':
    keywords = "Apple"
    category = "n:541966"
    price = 300.0
    price_range = 20.0
    a = search_results(keywords, category, price, price_range)
    f = open('extract.txt', 'w')
    while True:
        try:
            i = a.pop()._data
            f.write("\n")
            f.write(str(i['image']))
            f.write("\n")
            f.write(str(i['link']))
            f.write("\n")
            # f.write(str(i['title']))
            # f.write("\n")
            f.write(str(i['prime_price']))
            f.write("\n")
            f.write(str(i['new_price']))
            f.write("\n")
        except IndexError:
            break
    f.close()
