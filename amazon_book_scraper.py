import requests
from bs4 import BeautifulSoup


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_search_results(keywords="", rh='n:283155', page=None, min_p=None, price_range=20):
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
    if min_p is not None:
        params['low-price'] = min_p - (min_p * price_range / 100)
        params['high-price'] = min_p + (min_p * price_range / 100)
    resp = requests.get(base, params=params, timeout=5)
    resp.raise_for_status()
    return resp.content, resp.encoding


def extract_books(parsed, min_p, max_p):
    books = parsed.find_all('div', class_='result')
    print len(books)
    for book in books:
        img = book.find('div', class_='imageBox').find('img')
        link = book.find('div', class_='data').find('a')
        prime_price = book.find('td', class_= 'toeOurPrice')
        new_price = book.find('td', class_='toeNewPrice')
        i = item_dictionary(img, link, prime_price, new_price, min_p, max_p)
        if i is not None:
            yield i


def item_dictionary(img, link, prime_price, new_price, min_p, max_p):
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
        if int(np) >= min_p and int(np) <= max_p:
            item['new_price'] = new_price.string.strip()
            return item
        else:
            return None if item['prime_price'] == u'n/a' else item
    return None if item['prime_price'] == u'n/a' else item


if __name__ == '__main__':
    import pprint
    count = 0
    page = 1
    f = open('extract.txt', 'w')
    while count < 10:
        a = fetch_search_results("To Kill The Mocking Bird", 'n:283155', page, 50, 50)
        check = parse_source(a[0], 'utf-8').find_all('div', class_='result')
        if len(check) == 0:
            break
        b = extract_books(parse_source(a[0], 'utf-8'), 25, 75)
        for i in b:
            f.write(str(i) + "\n")
            count += 1
        page += 1
    f.close()
    '''
    a = u'http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=to+kill+a+mocking+bird&rh=n%3A283155%2Ck%3Ato+kill+a+mocking+bird&page=2'
    resp = requests.get(a, timeout=5)
    resp.raise_for_status()
    parsed = parse_source(resp.content, resp.encoding)
    next_link = parsed.find('a', id ='pagnNextLink')
    url = next_link.attrs['href']
    print next_link

    '''