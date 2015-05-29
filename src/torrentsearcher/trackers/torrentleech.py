import logbook
import pandas

from torrentsearcher.base.torrent_searcher import TorrentSearcher

logger = logbook.Logger(__name__)


class TorrentLeechSearcher(TorrentSearcher):
    base_url = "https://torrentleech.org/"
    query_url = "https://torrentleech.org/torrents/browse/index/query/"
    login_url = "https://torrentleech.org/user/account/login/"

    def __init__(self):
        super(TorrentLeechSearcher, self).__init__()
        self._is_logged_on = False

    def login(self, username, password):
        self.session.post(self.login_url,
                          data={'username': username,
                                'password': password,
                                'remember_me': 'on',
                                'login': 'submit'})
        logger.info("Logged on to Torrentleech with session_id {0}".format(self.session.cookies['PHPSESSID']))
        self._is_logged_on = True

    @property
    def is_logged_on(self):
        return self._is_logged_on

    def query_tracker(self, term, categories=()):
        if not self.is_logged_on:
            raise Exception('Need to login to TorrentLeech before searching')

        query_term_url = self.query_url + term
        resp = self.session.get(query_term_url, timeout=None)
        df = pandas.read_html(resp.text)

        # if we didn't get a DataFrame, we should have gotten a list of frames
        if isinstance(df, list):
            df = max(df, key=lambda frame: len(frame.columns))

        # clean it up a little bit
        df.dropna(axis=1, how='any', inplace=True)
        df.columns = ['name', 'comments', 'size', 'snatched', 'seeders', 'leechers']
        df.drop('comments', axis=1, inplace=True)
        return df.to_json()
