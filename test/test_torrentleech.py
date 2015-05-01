import pytest
import json
import os

from httmock import urlmatch, HTTMock, all_requests
from lxml.etree import XPath
from lxml.html import fromstring

from torrentsearcher.trackers.torrentleech import TorrentLeechSearcher

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')

with open(os.path.join(os.path.dirname(__file__), 'credentials.json')) as f:
    credentials_json = json.load(f)
    username, password = credentials_json['tl_username'], credentials_json['tl_password']


class TestTorrentLeech():

    USER_XPATH = XPath('//*[@id="memberBar"]/div[1]/b/a')

    @classmethod
    @pytest.fixture(scope='class', autouse=True)
    def setup(self):
        self.tl_searcher = TorrentLeechSearcher()

    def test_successful_connection(self):
        self.tl_searcher.login(username, password)
        html = fromstring(self.tl_searcher.session.get('http://torrentleech.org/user/messages').text)
        assert self.USER_XPATH(html)[0].get('href') == '/profile/' + username

    @urlmatch(scheme='https', netloc='torrentleech.org', path='/torrents/browse/index/query/game%20of%20thrones')
    def tl_game_of_thrones_mock(self, url, request):
        with open(os.path.join(SAMPLES_DIR,'torrentleech_query_game_of_thrones_results.html')) as c:
            return {'status_code': 200,
                    'content': c.read()}

    def test_getting_torrent_list(self):
        with HTTMock(self.tl_game_of_thrones_mock):
            parsed_results = json.loads(json.dumps(self.tl_searcher.query_tracker("game of thrones")))
            with open(os.path.join(SAMPLES_DIR, 'torrentleech_query_game_of_thrones_results.json')) as json_results:
                sample_results = json.load(json_results)
            assert sample_results == parsed_results
