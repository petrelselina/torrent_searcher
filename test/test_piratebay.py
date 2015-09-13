from itertools import islice
import logging

import vcr

import pytest

from torrentsearcher import PirateBaySearcher

__author__ = 'Omer'

logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from vcrpy
vcr_log = logging.getLogger("vcr")
vcr_log.setLevel(logging.INFO)


@pytest.mark.asyncio
@pytest.fixture
def piratebay_searcher(event_loop):
    searcher = PirateBaySearcher(loop=event_loop)
    return searcher


@pytest.yield_fixture
def sample_urls(piratebay_searcher):
    term = 'game of thrones'
    urls = ['{base}/{term}/{pagenum}/{action}/{category}'.format(base=piratebay_searcher.query_url,
                                                                 term=term,
                                                                 pagenum=0,
                                                                 action=99,
                                                                 category=0)] + \
           ['{base}/{term}/{pagenum}/{action}/{category}'.format(base=piratebay_searcher.query_url,
                                                                 term=term,
                                                                 pagenum=i,
                                                                 action=7,
                                                                 category=0) for i in range(1, 5)]
    yield urls


def test_piratebay_url_builder(piratebay_searcher, sample_urls):
    term = 'game of thrones'
    url_builder = piratebay_searcher._URLBuilderIterator(term, categories=piratebay_searcher.default_categories)
    urls = [_ for _ in islice(url_builder, 0, 5)]
    assert urls == [_ for _ in islice(sample_urls, 0, 5)]


@pytest.mark.asyncio
@vcr.use_cassette()
def test_piratebay_get_page(piratebay_searcher):
    test_url = 'https://thepiratebay.vg/search/ayreon%20The%20theory%20of%20everything/0/99/0'
    resp = yield from piratebay_searcher._get_page(test_url)
    assert len(resp) == 4


def test_piratebay_query_tracker(piratebay_searcher):
    results = piratebay_searcher.query_tracker('Taylor Swift 1989')
    assert len(results) > 1
