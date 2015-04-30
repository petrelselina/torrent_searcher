import json
import os
from lxml.etree import XPath
from lxml.html import fromstring

from torrentsearcher.trackers.torrentleech import TorrentLeechSearcher

with open(os.path.join(os.path.dirname(__file__), 'credentials.json')) as f:
    credentials_json = json.load(f)
    username, password = credentials_json['tl_username'], credentials_json['tl_password']


USER_XPATH = XPath('//*[@id="memberBar"]/div[1]/b/a')


def test_successful_connection():
    tl_searcher = TorrentLeechSearcher()
    tl_searcher.login(username, password)
    html = fromstring(tl_searcher.session.get('http://torrentleech.org/user/messages').text)
    assert USER_XPATH(html)[0].get('href') == '/profile/' + username
