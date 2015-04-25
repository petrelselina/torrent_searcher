import re
from humanfriendly import format_size
from humanfriendly import parse_size
import logbook
from lxml.etree import XPath
from lxml.html import fromstring

from src.base.torrent_searcher import TorrentSearcher
from src.base.utils import SIZE_REGEX

logger = logbook.Logger(__name__)


class TorrentLeechSearcher(TorrentSearcher):
    site_url = "https://torrentleech.org/"
    login_url = "https://torrentleech.org/user/account/login/"
    base_url = "https://torrentleech.org/torrents/browse/index/query/"

    table_xpath = XPath('//*[@id="torrenttable"]')
    link_xpath = XPath('td[2]/span[1]/a')
    seeders_xpath = XPath('td[7]')
    leechers_xpath = XPath('td[8]')
    size_xpath = XPath('td[5]')

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
        html = fromstring(resp.text)
        torrent_table = self.table_xpath(html)

        if torrent_table:
            with logger.catch_exceptions():
                # we skip tbody element
                for row in torrent_table[0][1]:
                    result = {
                        'name': self.link_xpath(row)[0].text_content(),
                        'link': self.link_xpath(row)[0].get('href'),
                        'seeders': self.seeders_xpath(row)[0].text_content(),
                        'leechers': self.leechers_xpath(row)[0].text_content(),
                        'size': ''
                    }
                    match = re.search(SIZE_REGEX, self.size_xpath(row)[0].text_content())
                    if match:
                        result['size'] = format_size(parse_size(match.group()))
                    results.append(result)
        return results
