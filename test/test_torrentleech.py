import json
import pytest

from pathlib import Path
from betamax import Betamax
from lxml.etree import XPath
from lxml.html import fromstring

from torrentsearcher.trackers.torrentleech import Tracker

with Betamax.configure() as config:
    config.cassette_library_dir = Path(__file__).parent.joinpath('fixtures', 'cassettes').__str__()

with Path(__file__).parent.joinpath('credentials.json').open() as f:
    credentials_json = json.load(f)
    username, password = credentials_json['tl_username'], credentials_json['tl_password']

USER_XPATH = XPath('//*[@id="memberBar"]/div[1]/b/a')


@pytest.fixture
def tl_searcher(request):
    tl_searcher = Tracker()
    session = tl_searcher.session
    betamax = Betamax(session, cassette_library_dir=config.cassette_library_dir)
    betamax.use_cassette(request.function.__name__)
    betamax.start()
    request.addfinalizer(betamax.stop)
    return tl_searcher


@pytest.fixture
def logged_in_tl_searcher(tl_searcher):
    tl_searcher.login(username, password)
    return tl_searcher


@pytest.fixture
def table(logged_in_tl_searcher):
    results = json.loads(logged_in_tl_searcher.query_tracker('game of thrones'))
    return results


def test_login(tl_searcher):
    """
    this tests if the PM page is visible (it should only be exposed to logged in users)
    """
    tl_searcher.login(username, password)
    html = fromstring(tl_searcher.session.get('http://torrentleech.org/user/messages').text)
    assert USER_XPATH(html)[0].get('href') == '/profile/' + username


def test_getting_torrent_list(table):
    assert len(table['name']) == 100
