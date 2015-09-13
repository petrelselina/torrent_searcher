from __future__ import unicode_literals, absolute_import, division, print_function

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
        return "<{} Torrents>".format(len(self.results))


class TorrentResult(object):
    def __init__(self, result):
        self.tracker = result['tracker']
        self.name = result['name']
        self.seeders = result['seeders']
        self.leechers = result['leechers']
        self.files = None
        self.num_files = None

        if result['torrent']:
            self.files = result['torrent'].files
            self.num_files = len(self.files)

    def __repr__(self):
        return "<{name} - Seeders : {seeders}, leechers {leechers} at {tracker}>".format(name=self.name,
                                                                                         seeders=self.seeders,
                                                                                         leechers=self.leechers,
                                                                                         tracker=self.tracker.name)
