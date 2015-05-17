import re
import pandas
from abc import abstractmethod, ABCMeta, abstractproperty

import logbook
from humanfriendly import format_size
from humanfriendly import parse_size
from lxml.html import fromstring

from requests import Session
from torrentsearcher.base.utils import get_latest_user_agent, SIZE_REGEX


logger = logbook.Logger(__name__)


class TorrentSearcher(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.session = Session()
        self.session.headers.update({'User-Agent': get_latest_user_agent("chrome")})

    @abstractmethod
    def login(self, username, password):
        """After the login, the session object should be initialized"""
        return

    @abstractproperty
    def link_xpath(self):
        pass

    @abstractproperty
    def seeders_xpath(self):
        pass

    @abstractproperty
    def leechers_xpath(self):
        pass

    @abstractproperty
    def table_xpath(self):
        pass

    @abstractproperty
    def size_xpath(self):
        pass

    @abstractproperty
    def query_url(self):
        """
        this url should refer to the address used for querying the tracker
        ex: https://thepiratebay.se/search/
        """
        pass

    @abstractproperty
    def base_url(self):
        pass

    def create_dataframe(self, term):
        query_term_url = self.query_url + term
        resp = self.session.get(query_term_url, timeout=None)
        df = pandas.read_html(resp.text)

        # if we didn't get a DataFrame, we should have gotten a list of frames
        if not type(df) == pandas.DataFrame:
            selected_frame = df[0]
            # select the biggest frame (should be the actual table)
            for d in df[1:]:
                if len(selected_frame.columns) < len(d.columns):
                    selected_frame = d
                else:
                    continue
            df = selected_frame

        # clean it up a little bit
        df.dropna(axis=1, how='any', inplace=True)
        return df

    def query_tracker(self, term):
        results = []
        query_term_url = self.query_url + term
        resp = self.session.get(query_term_url, timeout=None)
        html = fromstring(resp.text)

        torrent_table = self.table_xpath(html)

        if not torrent_table:
            logger.debug("Couldn't find torrent table in page {0}".format(query_term_url))
            return

        total_torrents = len(torrent_table[0])
        logger.debug("Found torrent table with {0} values".format(total_torrents))
        for index, row in enumerate(torrent_table[0]):
            try:
                logger.debug("Working on result {0}".format(index))
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

            except IndexError as e:
                # Exception is thrown when table headers is parsed..
                logger.exception(e)
                pass

        return results