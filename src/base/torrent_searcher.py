from abc import abstractmethod, ABCMeta

from requests import Session
from src.utils import get_latest_user_agent


class TorrentSearcher(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.session = Session()
        self.session.headers.update({'User-Agent': get_latest_user_agent("chrome")})

    @abstractmethod
    def login(self, username, password):
        """After the login, the session object should be initialized"""
        return

    def verify_login(self):
        """This should try and access a page only accessible to logged on members"""
        return
    #
    # @abstractproperty
    # def is_logged_on(self):
    #     return

    @abstractmethod
    def query_tracker(self, term):
        """This should return a dictionary with the following properties:
                - site_id
                - torrent_name
                - torrent_download_url
                - size
                - seeders
                - leechers
        """
        return