import re
import requests
from bs4 import BeautifulSoup

USER_AGENT_API_SITE = "http://www.useragentstring.com/pages/"
SIZE_REGEX = re.compile("{\d.}+(\s)?\wb", re.IGNORECASE)

def get_latest_user_agent(browser):
    html = requests.get(USER_AGENT_API_SITE + browser + '/')
    if html.status_code != 200:
        raise Exception("Couldn't fetch user agent string for {0}".format(browser))
    bs = BeautifulSoup(html.text)
    l = bs.find('div', attrs={'id': 'liste'})
    return l.find_all('ul')[0].text.strip()
