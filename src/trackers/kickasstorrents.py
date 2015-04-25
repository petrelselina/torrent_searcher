from lxml.etree import XPath
from src.base.torrent_searcher import TorrentSearcher


class KickAssTorrentsSearcher(TorrentSearcher):

    query_url = 'https://kickass.to/usearch/'
    base_url = 'https://kickass.to/'

    table_xpath = XPath('//*[@id="mainSearchTable"]/tr/td[1]/div[7]/table')
    link_xpath = XPath('td[1]/div[2]/div/a')
    seeders_xpath = XPath('td[5]')
    leechers_xpath = XPath('td[6]')
    size_xpath = XPath('td[2]')

    def __init__(self):
        super(KickAssTorrentsSearcher, self).__init__()

    def login(self, username, password):
        return
