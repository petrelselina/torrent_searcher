import re

import simplejson as json
from bs4 import BeautifulSoup
import logbook
import pandas
import zmq

from torrentsearcher import constants
from torrentsearcher.base.tracker import Tracker
from torrentsearcher.utils.torrent_info import TorrentClient, TorrentResolveMsg
from torrentsearcher.base.results import TorrentResultCollection

logger = logbook.Logger(__name__)

PIRATEBAY_SIZE_REGEX = "([\d.]+)([M,G]).?B"
size_re = re.compile(PIRATEBAY_SIZE_REGEX, re.IGNORECASE | re.UNICODE)


class PirateBaySearcher(Tracker):
    name = "Pirate Bay"
    base_url = "https://thepiratebay.se"
    query_url = "https://thepiratebay.se/search/"

    SEND_ADDR = constants.TORRENTS_IN_STREAM
    RECV_ADDR = constants.TORRENTS_OUT_STREAM

    def __init__(self):
        super().__init__()
        self._client = TorrentClient()
        self._client.start()
        self.context = zmq.Context.instance()
        self.recv_sock = self.context.socket(zmq.PULL)
        self.send_sock = self.context.socket(zmq.PUSH)
        self.send_sock.connect(self.SEND_ADDR)
        self.recv_sock.connect(self.RECV_ADDR)

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

        for result in dicts:
            result['tracker'] = self
            msg = TorrentResolveMsg(magnet_link=result['magnet'], timeout=30)
            msg.send_msg(self.send_sock)

        resolved_magnet_links = {}
        while len(resolved_magnet_links) <= len(dicts):
            result = self.recv_sock.recv_json()
            logger.info('Got response {status} for {id}'.format(status=result['status'],
                                                                id=result['id']))
            resolved_magnet_links[result['id']] = json.loads(result['object'])

        return TorrentResultCollection(results=dicts)
