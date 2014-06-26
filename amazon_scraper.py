import requests
import gevent
from bs4 import BeautifulSoup
from P_Queue import P_Queue


MIN_P = 0.0
MAX_P = 5000.0
FST_CLASS = u'fstRowGrid prod celwidget'
RSLT_CLASS = u'rsltGrid prod celwidget'
PP_CLASS = u'bld lrg red'
NP_CLASS = u'price bld'
DEPT_1 = {'All Departments': u'i:aps',
          'Kindle Store': u'n:133140011',
          'Movies & TV': u'n:2625373011',
          'Industrial & Scientific': u'n:16310091'}
DEPT_2 = {'Appliances': u'n:2619525011',
          'Arts, Crafts & Sewing': u'n:2617941011',
          'Automotive': u'n:15684181',
          'Baby': u'n:165796011',
          'Beauty': u'n:3760911',
          'Cell Phones & Accessories': u'n:2335752011',
          'Clothing & Accessories': u'n:1036592',
          'Collectibles & Fine Art': u'n:4991425011',
          'Computers': u'n:541966',
          'Electronics': u'n:172282',
          'Gift Cards Store': u'n:2238192011',
          'Grocery & Gourmet Food': u'n:16310101',
          'Health & Personal Care': u'n:3760901',
          'Home & Kitchen': u'n:1055398',
          'Jewelry': u'n:3367581',
          'Musical Instruments': u'n:11091801',
          'Office Products': u'n:1064954',
          'Patio, Lawn & Garden': u'n:2972638011',
          'Pet Supplies': u'n:2619533011',
          'Shoes': u'n:672123011',
          'Sports & Outdoors': u'n:3375251',
          'Tools & Home Improvement': u'n:228013',
          'Toys & Games': u'n:165793011',
          'Watches': u'n:377110011',
          'Wine': u'n:2983386011'}


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_search_results(keywords="",
                         rh='n:172282',
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
    fst = parsed.find_all('div', class_=FST_CLASS)
    rslt = parsed.find_all('div', class_=RSLT_CLASS)
    for block in fst:
        img = block.find('div', class_='imageBox').find('img')
        link = block.find('h3', class_='newaps').find('a')
        prime_price = block.find('span', class_=PP_CLASS)
        new_price = block.find('span', class_=NP_CLASS)
        item = item_dictionary(img, link, prime_price, new_price)
        if item is not None:
            yield item
    for block in rslt:
        img = block.find('div', class_='imageBox').find('img')
        link = block.find('h3', class_='newaps').find('a')
        prime_price = block.find('span', class_=PP_CLASS)
        new_price = block.find('span', class_=NP_CLASS)
        item = item_dictionary(img, link, prime_price, new_price)
        if item is not None:
            yield item


def get_price(price_string):
    if price_string is not None:
        x = price_string.string.strip()
        if '-' in x:
            x = x.split(' - ')[0]
        if '$' in x:
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


def set_globals(category, price, price_range):
    global MIN_P
    global MAX_P
    global FST_CLASS
    global RSLT_CLASS
    global PP_CLASS
    global NP_CLASS
    if len(str(price)) > 0:
        price = float(price)
        price_range = float(price_range)
        MIN_P = price - (price * price_range / 100)
        MAX_P = price + (price * price_range / 100)
    if str(category) in DEPT_1:
        FST_CLASS = u'fstRow prod celwidget'
        RSLT_CLASS = u'rslt prod celwidget'
        return DEPT_1[category]
    FST_CLASS = u'fstRowGrid prod celwidget'
    RSLT_CLASS = u'rsltGrid prod celwidget'
    return DEPT_2[category]


def page_scrape(keywords, category, page, p_queue):
    content = fetch_search_results(keywords,
                                   category,
                                   page)
    parsed = parse_source(content[0], content[1])
    items = extract_items(parsed)
    for i in items:
        pri = 0
        if i['prime_price'] == u'n/a':
            pri = int(i['new_price'][1:-3].replace(',', ''))
        else:
            pri = int(i['prime_price'][1:-3].replace(',', ''))
        p_queue.insert(i, pri)


def search_results(keywords, category, price, price_range):
    page = 1
    category = set_globals(category, price, price_range)
    p_queue = P_Queue()
    while p_queue._size < 5:
        temp = p_queue._size
        gevent.joinall([
            gevent.spawn(page_scrape(keywords, category, page+2, p_queue)),
            gevent.spawn(page_scrape(keywords, category, page+1, p_queue)),
            gevent.spawn(page_scrape(keywords, category, page, p_queue))
            ])
        page += 3
        if p_queue._size == temp and p_queue._size > 0:
            break
    return p_queue


if __name__ == '__main__':
    keywords = "Apple"
    category = "Electronics"
    price = 500.0
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
