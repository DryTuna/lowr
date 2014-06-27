import pytest
from amazon_scraper import search_results
from amazon_scraper import parse_source
from amazon_scraper import extract_items
from amazon_scraper import get_price
from amazon_scraper import item_dictionary


@pytest.fixture(scope='module')
def set_parser(request):
    a = open('amazon_sample.html', 'r')
    parsed = parse_source(a, 'UTF-8')
    a.close()
    return parsed


def test_parse_source(set_parser):
    parsed = set_parser
    assert len(parsed.find_all('div', class_='fstRow prod celwidget')) == 1


def test_extract_item(set_parser):
    parsed = set_parser
    for i in extract_items(parsed):
        assert isinstance(i['image'], str)
        assert isinstance(i['link'], str)
        assert i['prime_price'] == 'n/a' or isinstance(i['prime_price'], float)
        assert i['new_price'] == 'n/a' or isinstance(i['new_price'], float)


def test_get_price(set_parser):
    parsed = set_parser
    fst = parsed.find_all('div', class_='fstRow prod celwidget')
    prime_price = fst[0].find('span', class_='bld lrg red')
    new_price = fst[0].find('span', class_='price bld')
    assert get_price(prime_price) == '$348.43'
    assert get_price(new_price) == '$305.00'


def test_item_dictionary(set_parser):
    parsed = set_parser
    fst = parsed.find_all('div', class_='fstRow prod celwidget')
    img = fst[0].find('div', class_='imageBox').find('img')
    link = fst[0].find('h3', class_='newaps').find('a')
    prime_price = fst[0].find('span', class_='bld lrg red')
    new_price = fst[0].find('span', class_='price bld')
    item = item_dictionary(img, link, prime_price, new_price)
    assert item['image'] == 'http://ecx.images-amazon.com/images/I/41Hi9DIctiL._AA160_.jpg'
    assert item['link'] == 'http://www.amazon.com/Dell-Inspiron-15-6-Inch-i15RV-954BLK-Version/dp/B00HRLSSKO'
    assert item['title'] == 'Dell Inspiron 15.6-Inch Laptop (i15RV-954BLK) (Old Version)'
    assert item['prime_price'] == '$348.43'
    assert item['new_price'] == '$305.00'


def test_search_results():
    keywords = "Apple"
    category = "Electronics"
    price = 1000.0
    price_range = 50.0
    a = search_results(keywords, category, price, price_range)
    assert a._size > 10
