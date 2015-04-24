import logbook

from bs4 import BeautifulSoup
from src.base.torrent_searcher import TorrentSearcher
from src.base.utils import SIZE_REGEX

logger = logbook.Logger(__name__)


class TorrentLeechSearcher(TorrentSearcher):
    site_url = "https://torrentleech.org/"
    login_url = "https://torrentleech.org/user/account/login/"
    base_url = "https://torrentleech.org/torrents/browse/index/query/"

    def __init__(self):
        super(TorrentLeechSearcher, self).__init__()

    def login(self, username, password):
        self.session.post(self.login_url,
                          data={'username': username,
                                'password': password,
                                'remember_me': 'on',
                                'login': 'submit'})
        logger.info("Logged on to Torrentleech with session_id {0}".format(self.session.cookies['PHPSESSID']))

    def query_tracker(self, term):
        results = []
        resp = self.session.get(self.base_url + term, timeout=None)
        bs = BeautifulSoup(resp.text, "html5lib")

        torrent_table = bs.find('table', attrs={'id': 'torrenttable'})

        if torrent_table:
            rows = torrent_table('tr')
            # Skip header row
            logger.debug("Found {0} results on page".format(len(rows) - 1))
            for index, row in enumerate(rows[1:]):
                with logger.catch_exceptions():
                    link = row.find('td', attrs={'class': 'name'})
                    if link:
                        logger.debug("working on: " + link.a.text)
                        results.append({
                            'id': link.a['href'].replace('/torrent/', ''),
                            'name': link.a.text,
                            'url': row.find('td', attrs={'class': 'quickdownload'}).a['href'],
                            'size': row.find_next(text=SIZE_REGEX),
                            'seeders': int(row.find('td', attrs={'class': 'seeders'}).text),
                            'leechers': int(row.find('td', attrs={'class': 'leechers'}).text),
                        })
                    else:
                        logger.debug("could not find info on row {0}".format(index))
                        continue
            logger.debug("Successfully processed {0} results".format(len(results)))
        else:
            logger.error("Could not find the torrent table!")
        return results
