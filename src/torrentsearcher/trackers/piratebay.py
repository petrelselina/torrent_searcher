import logbook
import pandas
import re

from torrentsearcher.base.torrent_searcher import TorrentSearcher


logger = logbook.Logger(__name__)

PIRATEBAY_SIZE_REGEX = "([\d.]+)([M,G]).?B"
size_re = re.compile(PIRATEBAY_SIZE_REGEX, re.IGNORECASE | re.UNICODE)

class PirateBaySearcher(TorrentSearcher):
    base_url = "https://thepiratebay.se"
    query_url = "https://thepiratebay.se/search/"

    def __init__(self):
        super(PirateBaySearcher, self).__init__()

    def login(self, username, password):
        return

    @staticmethod
    def get_size_from_name_string(name):
        size_tuple = size_re.findall(name)[0]
        size = None

        if not size_tuple:
            return size
        if size_tuple[1] == 'M':
            size = float(size_tuple[0])
        if size_tuple[1] == 'G':
            size = float(size_tuple[0])*1024

        return size

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

        df['name'] = df.name.apply(lambda x: x.replace(u'\xa0', u''))
        df['size'] = df.name.apply(self.get_size_from_name_string)

        return df.to_json()
