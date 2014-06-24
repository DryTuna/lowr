import requests
from bs4 import BeautifulSoup


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_search_results(title="", dept='&rh=n:283155', min_p=None, range=20):
    search_params = {
        key: val for key, val in locals().items() if val is not None
    }
    if not search_params:
        raise ValueError("No valid keywords")
    base = 'http://www.amazon.com/s/ref=sr_st_relevancerank'
    if len(title) == 0:
        raise ValueError("Please enter search keys")
    base += '?keywords='+title
    base += dept
    if min_p is not None:
        base += '&low-price='+str(min_p - (min_p * range / 100))
        base += '&high-price='+str(min_p + (min_p * range / 100))
    resp = requests.get(base, timeout=5)
    resp.raise_for_status()
    return resp.content, resp.encoding


def fetch_next(content):
    next_link = content.find('a', class_='pagnNext')
    url = next_link.attrs['href']
    resp = requests.get(url, timeout=5)
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


if __name__ == '__main__':
    import pprint
    a = fetch_search_results("To kill a mocking bird",'&rh=n:283155', 50, 50)
    b = extract_books(parse_source(a[0], 'utf-8'), 25, 75)
    f = open('extract.txt', 'w')
    for i in b:
        f.write(str(i) + "\n")
        pprint.pprint(i)
    f.close()
