import requests
from bs4 import BeautifulSoup


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_search_results(title="", min_p=None, max_p=None):
    search_params = {
        key: val for key, val in locals().items() if val is not None
    }
    if not search_params:
        raise ValueError("No valid keywords")
    base = 'http://www.amazon.com/s/ref=sr_st_relevancerank'
    if len(title) == 0:
        raise ValueError("Please enter search keys")
    base += '?keywords='+title
    base += '&rh=n:283155'
    if min_p is not None:
        base += '&low-price='+str(min_p)
    if max_p is not None:
        base += '&high-price='+str(max_p)
    resp = requests.get(base, timeout=5)
    resp.raise_for_status()
    return resp.content, resp.encoding


def extract_books(parsed):
    books = parsed.find_all('div', class_='result')
    print len(books)
    extracted = []
    for book in books:
        img = book.find('div', class_='image').find('a')
        link = book.find('div', class_='data').find('a')
        price = book.find('td', class_='toeNewPrice')
        this_book = {
            'image': img.attrs['href'],
            'link': link.attrs['href'],
            'title': link.string.strip(),
            'price': price
        }
        extracted.append(this_book)
    return extracted


if __name__ == '__main__':
    import pprint
    a = fetch_search_results("To kill a mocking bird", 50, 100)
    b = extract_books(parse_source(a[0], 'utf-8'))
    f = open('extract.txt', 'w')
    f.close()
    pprint.pprint(b[0])
