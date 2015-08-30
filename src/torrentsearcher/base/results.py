from __future__ import unicode_literals, absolute_import, division, print_function

from .tracker import Tracker

__author__ = 'Omer'


class TorrentResultCollection(object):
    def __init__(self, results):
        self.results = results

    def __iter__(self):
        return self.results

    def as_dataframe(self):
        raise NotImplementedError()

    def __repr__(self):
        return "<{} Torrents>"


class TorrentResult(object):
    def __init__(self, name, seeders, leechers, link, tracker):
        assert isinstance(tracker, Tracker), "Tracker must be an instance of tracker object!"
        self.tracker = tracker
        self.name = name
        self.seeders = seeders
        self.leechers = leechers
        self.link = link

    def __repr__(self):
        return "<{name} - Seeders : {seeders}, leechers {leechers} at {tracker}>".format(name=self.name,
                                                                                         seeders=self.seeders,
                                                                                         leechers=self.leechers,
                                                                                         tracker=self.tracker.name)
