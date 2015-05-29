from abc import abstractmethod, ABCMeta, abstractproperty

import logbook
from requests import Session

from torrentsearcher.base.utils import get_latest_user_agent

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
    def query_url(self):
        """
        this url should refer to the address used for querying the tracker
        ex: https://thepiratebay.se/search/
        """
        pass

    @abstractproperty
    def base_url(self):
        pass

    @abstractmethod
    def query_tracker(self, term, categories=()):
        pass
