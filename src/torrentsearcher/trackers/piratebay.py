import re

from bs4 import BeautifulSoup

import logbook
import pandas

from torrentsearcher.base.tracker import Tracker
from torrentsearcher.utils.torrent_info import TorrentClient
from torrentsearcher.base.results import TorrentResultCollection

logger = logbook.Logger(__name__)

PIRATEBAY_SIZE_REGEX = "([\d.]+)([M,G]).?B"
size_re = re.compile(PIRATEBAY_SIZE_REGEX, re.IGNORECASE | re.UNICODE)


class PirateBaySearcher(Tracker):
    base_url = "https://thepiratebay.se"
    query_url = "https://thepiratebay.se/search/"

    def __init__(self):
        super(PirateBaySearcher, self).__init__()
        self._client = None

    def login(self, username, password):
        return

    @staticmethod
    def _get_size_from_name_string(name):
        name = name.replace(u'\xa0', u'')
        size_tuple = size_re.findall(name)

        if not size_tuple:
            return

        size_tuple = size_tuple[0]

        size = None

        if not size_tuple:
            return size
        if size_tuple[1] == 'M':
            size = float(size_tuple[0])
        if size_tuple[1] == 'G':
            size = float(size_tuple[0]) * 1024

        return size

    @staticmethod
    def _clean_name(name):
        return name.replace(u'\xa0', u'').split('Uploaded')[0].strip()

    def query_tracker(self, term=None, exclude_query=None, categories=None, results_limit=None):
        query_term_url = self.query_url + term
        resp = self.session.get(query_term_url, timeout=None)
        df = pandas.read_html(resp.text)  # if we didn't get a DataFrame, we should have gotten a list of frames
        soup = BeautifulSoup(resp.text)

        if isinstance(df, list):
            df = max(df, key=lambda frame: len(frame.columns))

        # clean it up a little bit
        df.dropna(axis=1, how='any', inplace=True)
        df.columns = ['type', 'name', 'seeders', 'leechers']
        df.drop('type', axis=1, inplace=True)

        df['size'] = df.name.apply(self._get_size_from_name_string)
        df['name'] = df.name.apply(self._clean_name)

        magnets = list(
            map(lambda x: x['href'], soup.find_all('a', href=re.compile('magnet.+', re.IGNORECASE | re.UNICODE))))

        df.insert(loc=4, column='magnet', value=magnets)

        dicts = df.to_dict('records')

        if not self._client:
            self._client = TorrentClient()

        client = self._client

        for result in dicts:
            result['tracker'] = self
            result['torrent'] = client.torrent_from_magnet_link(result['magnet'])

        return TorrentResultCollection(results=dicts)
