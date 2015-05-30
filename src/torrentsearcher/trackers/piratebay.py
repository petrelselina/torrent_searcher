import logbook
from lxml.etree import XPath
import pandas

from torrentsearcher.base.torrent_searcher import TorrentSearcher


logger = logbook.Logger(__name__)


class PirateBaySearcher(TorrentSearcher):
    base_url = "https://thepiratebay.se"
    query_url = "https://thepiratebay.se/search/"

    def __init__(self):
        super(PirateBaySearcher, self).__init__()

    def login(self, username, password):
        return

    def query_tracker(self, term, categories=()):
        query_term_url = self.query_url + term
        resp = self.session.get(query_term_url, timeout=None)
        df = pandas.read_html(resp.text)

        # if we didn't get a DataFrame, we should have gotten a list of frames
        if isinstance(df, list):
            df = max(df, key=lambda frame: len(frame.columns))

        # clean it up a little bit
        df.dropna(axis=1, how='any', inplace=True)
        df.columns = ['type', 'name', 'seeders', 'leechers']
        df.drop('type', axis=1, inplace=True)
        return df.to_json()
