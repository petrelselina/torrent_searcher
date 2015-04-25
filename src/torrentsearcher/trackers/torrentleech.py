import logbook
from lxml.etree import XPath

from torrentsearcher.base.torrent_searcher import TorrentSearcher


logger = logbook.Logger(__name__)


class TorrentLeechSearcher(TorrentSearcher):
    base_url = "https://torrentleech.org/"
    query_url = "https://torrentleech.org/torrents/browse/index/query/"

    login_url = "https://torrentleech.org/user/account/login/"

    table_xpath = XPath('//*[@id="torrenttable"]/tbody')
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