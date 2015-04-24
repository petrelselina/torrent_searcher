import re
import logbook
from src.base.torrent_searcher import TorrentSearcher
from src.base.utils import SIZE_REGEX
from lxml.html import fromstring
from lxml.etree import XPath

logger = logbook.Logger(__name__)


class PirateBaySearcher(TorrentSearcher):
    site_url = "https://thepiratebay.se"
    base_url = "https://thepiratebay.se/search/"

    table_xpath = XPath('//*[@id="searchResult"]')
    link_xpath = XPath('td[2]/div/a')
    seeders_xpath = XPath('td[3]')
    leechers_xpath = XPath('td[4]')
    info_xpath = XPath('td[2]/font')

    def __init__(self):
        super(PirateBaySearcher, self).__init__()

    def login(self, username, password):
        return

    def query_tracker(self, term):
        results = []
        resp = self.session.get(self.base_url + term, timeout=None)
        html = fromstring(resp.text)
        torrent_table = self.table_xpath(html)

        if torrent_table:
            with logger.catch_exceptions():
                for row in torrent_table[0][1:]:
                    result = {
                        'name': self.link_xpath(row)[0].text_content(),
                        'link': self.link_xpath(row)[0].get('href'),
                        'seeders': self.seeders_xpath(row)[0].text_content(),
                        'leechers': self.leechers_xpath(row)[0].text_content(),
                        'size': ''
                    }
                    match = re.search(SIZE_REGEX, self.info_xpath(row)[0].text_content())
                    if match:
                        result['size'] = match.string
                    results.append(result)
        return results