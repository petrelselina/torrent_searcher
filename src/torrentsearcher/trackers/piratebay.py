import contextlib
from enum import Enum, unique
from itertools import islice
import re
import warnings
import asyncio
from asyncio import coroutine
import sys

import aiohttp

from bs4 import BeautifulSoup
import logbook
import pandas

from torrentsearcher.base.tracker import Tracker

logger = logbook.Logger(__name__)
logger.handlers.append(logbook.StreamHandler(sys.stdout))

PIRATEBAY_SIZE_REGEX = "([\d.]+)([M,G]).?B"
BATCH_SIZE = 5
size_re = re.compile(PIRATEBAY_SIZE_REGEX, re.IGNORECASE | re.UNICODE)


@unique
class PirateBayCategories(Enum):
    All = '0'

    @unique
    class Audio(Enum):
        Music = '101'
        Audio_Books = '102'
        Sound_Clips = '103'
        FLAC = '104'
        Other = '199'

    @unique
    class Video(Enum):
        Movies = '201'
        Movies_DVDR = '202'
        Music_Videos = '203'
        Movie_Clips = '204'
        TV_Shows = '205'
        Handheld = '206'
        HD_Movies = '207'
        HD_TV_Shows = '208'
        Movies_3D = '209'
        Other = '299'

    @unique
    class Applications(Enum):
        Windows = '301'
        Mac = '302'
        UNIX = '303'
        Others = '399'

    @unique
    class Games(Enum):
        PC = '401'
        Mac = '402'
        PSx = '403'
        XBOX360 = '404'
        Wii = '405'
        Handheld = '406'
        IOS_iPad_iPhone = '407'
        Android = '408'
        Other = '499'

    @unique
    class Other(Enum):
        Ebooks = '601'
        Comics = '602'
        Pictures = '603'
        Covers = '604'
        Physibles = '605'
        Other = '699'


class PirateBayExceptionBase(Exception):
    pass


class NoResultsException(PirateBayExceptionBase):
    pass


class PirateBaySearcher(Tracker):
    name = "Pirate Bay"
    base_url = "https://thepiratebay.se"
    query_url = "https://thepiratebay.se/search"
    default_categories = [PirateBayCategories.All]

    def __init__(self, loop=None):
        super().__init__()
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.sem = asyncio.Semaphore(BATCH_SIZE)

    def login(self, username, password):
        return

    # ------------- PARSE LOGIC ----------------------
    @staticmethod
    def _get_size_from_name_string(name):
        name = name.replace(u'\xa0', u'')
        size_tuple = size_re.findall(name)

        if not size_tuple:
            return

        size_tuple = size_tuple[0]

        size = None

        if not size_tuple:
            return size
        if size_tuple[1] == 'M':
            size = float(size_tuple[0])
        if size_tuple[1] == 'G':
            size = float(size_tuple[0]) * 1024

        return size

    @staticmethod
    def _clean_name(name):
        return name.replace(u'\xa0', u'').split('Uploaded')[0].strip()

    def _parse_page(self, page_text):
        try:
            df = pandas.read_html(page_text, attrs={'id': 'searchResult'})
        except ValueError:
            logger.debug('No tables found in page')
            raise NoResultsException()

        df = df[0]
        # clean it up a little bit
        df.dropna(axis=1, how='any', inplace=True)
        df.columns = ['type', 'name', 'seeders', 'leechers']
        df.drop('type', axis=1, inplace=True)

        df['size'] = df.name.apply(self._get_size_from_name_string)
        df['name'] = df.name.apply(self._clean_name)

        df.insert(loc=4, column='magnet', value=self._get_all_magnet_links_in_page(page_text=page_text))

        return df.to_dict('records')

    @staticmethod
    def _get_all_magnet_links_in_page(page_text):
        soup = BeautifulSoup(page_text)
        magnets = list(
            map(lambda x: x['href'], soup.find_all('a', href=re.compile('magnet.+', re.IGNORECASE | re.UNICODE))))
        return magnets

    # -------------------------------------------------

    @coroutine
    def _get_page(self, page):
        logger.debug('Going to fetch page {}'.format(page))
        with (yield from self.sem):
            resp = yield from self.session.get(page)
            if resp.status != 200:
                logger.warning('Bad status code {code} at page {page}'.format(code=resp.status,
                                                                              page=page))
                self.sem.release()
                return None

            text = yield from resp.text()
            results = self._parse_page(text)

        return results

    def query_tracker(self, term=None, exclude_term=None, categories=None, results_limit=25, timeout=15):
        category = categories
        res = []
        page_counter = 0
        stop = False
        while len(res) <= results_limit or not stop:
            url_builder = self._URLBuilderIterator(term=term, categories=category)
            coros = (self._get_page(page) for page in islice(url_builder, page_counter, page_counter + BATCH_SIZE))
            done, _ = self.loop.run_until_complete(asyncio.wait([self.loop.create_task(coro) for coro in coros]))
            for coro in done:
                if coro.exception() is not None:
                    stop = True
                    continue
                else:
                    res.extend(coro.result())

        return res

    class _URLBuilderIterator(object):
        def __init__(self, term, categories):
            self.term = term
            self.categories = categories or PirateBaySearcher.default_categories
            self.pagenum = 0

        def __iter__(self):
            return self

        def __next__(self):
            url = self.build_url(term=self.term,
                                 categories=self.categories,
                                 pagenum=self.pagenum,
                                 action=99 if self.pagenum == 0 else 7)
            self.pagenum += 1
            return url

        def build_url(self, term=None, categories=None, pagenum=0, action=99):
            assert term, 'function must be called with term'
            assert categories, 'function must be invoked with category'
            category = categories[0]

            if len(categories) > 1:
                warnings.warn("PirateBay supports only one category, defaulting to all")
                category = PirateBaySearcher.default_categories

            return '{base}/{term}/{pagenum}/{action}/{category}'.format(base=PirateBaySearcher.query_url,
                                                                        term=term,
                                                                        pagenum=pagenum,
                                                                        action=action,
                                                                        category=category.value)
