from __future__ import unicode_literals, absolute_import, division, print_function
from torrentsearcher.utils.torrent_info import Torrent

from .tracker import Tracker

__author__ = 'Omer'


class TorrentResultCollection(object):
    def __init__(self, results=None):
        self.results = []
        if results is not None:
            for result in results:
                self.results.append(TorrentResult(result))

    def __iter__(self):
        return self.results

    def as_dataframe(self):
        raise NotImplementedError()

    def __repr__(self):
        return "<{} Torrents>"


class TorrentResult(object):
    def __init__(self, result):
        assert isinstance(result['tracker'], Tracker), "Tracker must be an instance of tracker object!"
        self.tracker = result['tracker']
        self.name = result['name']
        self.seeders = result['seeders']
        self.leechers = result['leechers']
        #self.link = result['link']
        assert isinstance(result['torrent'], Torrent), "Tracker must be an instance of tracker object!"
        self._torrent = result['torrent']

        self.num_files = len(self._torrent.files)

    def __repr__(self):
        return "<{name} - Seeders : {seeders}, leechers {leechers} at {tracker}>".format(name=self.name,
                                                                                         seeders=self.seeders,
                                                                                         leechers=self.leechers,
                                                                                         tracker=self.tracker.name)
