import logbook
from lxml.etree import XPath

from src.base.torrent_searcher import TorrentSearcher


logger = logbook.Logger(__name__)


class PirateBaySearcher(TorrentSearcher):
    base_url = "https://thepiratebay.se"
    query_url = "https://thepiratebay.se/search/"

    table_xpath = XPath('//*[@id="searchResult"]')
    link_xpath = XPath('td[2]/div/a')
    seeders_xpath = XPath('td[3]')
    leechers_xpath = XPath('td[4]')
    size_xpath = XPath('td[2]/font')

    def __init__(self):
        super(PirateBaySearcher, self).__init__()

    def login(self, username, password):
        return
