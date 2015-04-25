import re
import requests
from bs4 import BeautifulSoup

USER_AGENT_API_SITE = "http://www.useragentstring.com/pages/"
SIZE_REGEX = re.compile("[\d.]+\s?\w{1,2}b", re.IGNORECASE + re.UNICODE)


def get_latest_user_agent(browser):
    """This function retrieves the latest user-agent string for the given browser"""
    html = requests.get(USER_AGENT_API_SITE + browser + '/')
    html.raise_for_status()
    bs = BeautifulSoup(html.text)
    l = bs.find('div', attrs={'id': 'liste'})
    return l.find_all('ul')[0].text.strip()
