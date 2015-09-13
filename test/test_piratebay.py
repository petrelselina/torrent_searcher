from itertools import islice
from pathlib import Path

from betamax import Betamax

import pytest

from torrentsearcher import PirateBaySearcher

__author__ = 'Omer'

with Betamax.configure() as config:
    config.cassette_library_dir = Path(__file__).parent.joinpath('fixtures', 'cassettes').__str__()


@pytest.fixture
def piratebay_searcher(request):
    searcher = PirateBaySearcher()
    session = searcher.session
    betamax = Betamax(session, cassette_library_dir=config.cassette_library_dir)
    betamax.use_cassette(request.function.__name__)
    betamax.start()
    request.addfinalizer(betamax.stop)
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


def test_piratebay_get_page(piratebay_searcher):
    test_url = 'https://thepiratebay.vg/search/ayreon%20The%20theory%20of%20everything/0/99/0'
    resp = piratebay_searcher._get_page(test_url)
    assert len(resp) == 4


def test_piratebay_query_tracker(piratebay_searcher):
    results = piratebay_searcher.query_tracker('game of thrones')
    assert len(results) > 1
