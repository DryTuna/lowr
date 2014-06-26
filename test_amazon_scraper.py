from amazon_scraper import fetch_search_results
from amazon_scraper import parse_source
from amazon_scraper import extract_items
from amazon_scraper import search_results


def test_scraper():
    keywords = "Apple"
    category = "n:172282"

    content = fetch_search_results(keywords, category)
    assert 'DOCTYPE html' in content[0]
    assert content[1] == 'UTF-8'

    parsed = parse_source(content[0], content[1])
    assert 'DOCTYPE html' in content[0]

    items = extract_items(parsed)
    for i in items:
        assert 'image' in i
        assert 'link' in i


def test_search_results():
    keywords = "Apple"
    category = "Electronics"
    price = 1000.0
    price_range = 50.0
    a = search_results(keywords, category, price, price_range)
    assert a._size > 10


