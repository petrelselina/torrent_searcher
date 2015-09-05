import tempfile
import time

import libtorrent as lt

from torrentsearcher.utils.misc import pretty_size


class TorrentClient(object):
    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.session = lt.session()
        self.params = {
            'save_path': self.tempdir,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True
        }

    def torrent_from_magnet_link(self, magnet_link):
        handle = lt.add_magnet_uri(self.session, magnet_link, self.params)
        # callback/blocking call is not implemented for magnet links
        while not handle.has_metadata():
            time.sleep(0.1)

        return Torrent(handle)


class Torrent(object):
    def __init__(self, handle):
        self.info = handle.get_torrent_info()
        self._files = self.info.files()
        self.files = [TorrentInnerFile(f) for f in self._files]
        self.name = self.info.name()
        self.comment = self.info.comment()
        self.size = self.info.total_size()

    def __iter__(self):
        for file in self.files:
            yield file

    @property
    def size_pretty(self):
        return pretty_size(self.size)

    def __repr__(self):
        return "<{name} - {num_files} files: Total {size}>".format(name=self.name,
                                                                   num_files=len(self.files),
                                                                   size=self.size_pretty)


class TorrentInnerFile(object):
    def __init__(self, libtorrent_file_object):
        self.size = libtorrent_file_object.size
        self.path = libtorrent_file_object.path
        self.name = self.path.split('\\')[-1]

    @property
    def size_pretty(self):
        return pretty_size(self.size)

    def __repr__(self):
        return "<{name} - size : {size}>".format(name=self.name,
                                                 size=self.size_pretty)
