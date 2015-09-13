import struct
import tempfile
import threading
import time
from collections import namedtuple
from enum import Enum
import sys

import simplejson as json
import zmq
import libtorrent as lt
from zmq.eventloop import IOLoop

from zmq.eventloop.ioloop import PeriodicCallback

from zmq.eventloop.zmqstream import ZMQStream
import logbook

from torrentsearcher import constants
from torrentsearcher.utils.misc import pretty_size


class TorrentTask(namedtuple('TorrentTask', ['magnet_link', 'id', 'handle', 'timeout'])):
    pass


class TorrentResolveMsg(namedtuple('TorrentResolveMsg', ['magnet_link', 'timeout'])):
    def send_msg(self, socket):
        magnet_link = self.magnet_link.encode('utf-8')
        timeout = struct.pack('!q', self.timeout)
        socket.send_multipart([magnet_link, timeout])

    @classmethod
    def recv(cls, socket):
        """Reads message from socket, returns new TorrentResolveMsg instance."""
        return cls.from_msg(socket.recv_multipart())

    @classmethod
    def from_msg(cls, msg):
        magnet_link, timeout = msg
        magnet_link = magnet_link if magnet_link else None
        timeout = struct.unpack('!q', timeout)[0]
        return cls(magnet_link=magnet_link, timeout=timeout)


class TaskStatus(Enum):
    ERROR = -1
    SUCCESS = 0
    TIMEOUT = 1


class Commands(Enum):
    SHUTDOWN = '1'
    STOP = '2'


class TorrentClient(threading.Thread):
    SEND_ADDR = constants.TORRENTS_OUT_STREAM
    RECV_ADDR = constants.TORRENTS_IN_STREAM

    def __init__(self, ctx=None, loop=None):
        super(TorrentClient, self).__init__()
        self.tempdir = tempfile.mkdtemp()
        self.session = lt.session()
        self.params = {
            'save_path': self.tempdir,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True
        }
        self.tasks = []
        self.loop = loop or IOLoop.instance()
        self.recv_stream = None
        self.send_sock = None
        self.recv_sock = None
        self.logger = logbook.Logger(__name__)
        self.logger.handlers.append(logbook.StreamHandler(sys.stdout))
        self.ctx = ctx or zmq.Context.instance()

    def run(self):
        self.recv_sock = self.ctx.socket(zmq.PULL)
        self.recv_sock.bind(self.RECV_ADDR)

        self.send_sock = self.ctx.socket(zmq.PUSH)
        self.send_sock.bind(self.SEND_ADDR)

        self.recv_stream = ZMQStream(self.recv_sock, io_loop=self.loop)

        self.recv_stream.on_recv(self._add_magnet_link_resolve_task)

        check_callback = PeriodicCallback(self._check_all_torrents, 1000, self.loop)

        check_callback.start()
        self.logger.info('Starting eventloop')
        self.loop.start()

    def _check_all_torrents(self):
        self.logger.debug('Checking torrents status')
        for task in self.tasks:
            # callback/blocking call is not implemented for magnet links
            self.logger.debug('Checking task {id}'.format(id=task.id))
            if task.handle.has_metadata():
                self.logger.info('Done working on task {id}'.format(id=task.id))
                self.send_sock.send_json({'response': TaskStatus.SUCCESS.value,
                                          'id': task.id,
                                          'object': json.dumps(
                                              Torrent(handle=task.handle, magnet_id=task.id).to_dict())})

                self.session.remove_torrent(task.handle)
                self.tasks.remove(task)
            elif time.time() > task.timeout:
                self.logger.warning('Timeout on task {id}'.format(id=task.id))
                self.send_sock.send_json({'response': TaskStatus.TIMEOUT.value,
                                          'id': task.id,
                                          'object': None})

                self.session.remove_torrent(task.handle)
                self.tasks.remove(task)
            else:
                self.logger.debug('Task {} is not ready yet'.format(task.id))

    def _add_magnet_link_resolve_task(self, msg):
        msg = TorrentResolveMsg.from_msg(msg)
        magnet_link, timeout = msg.magnet_link, msg.timeout
        handle = lt.add_magnet_uri(self.session, magnet_link, self.params)
        self.tasks.append(
            TorrentTask(magnet_link=magnet_link,
                        id=magnet_link[20:60],
                        handle=handle,
                        timeout=time.time() + timeout))

    def stop(self):
        self.loop.stop()
        self.join()
        self.send_sock.close()
        self.recv_sock.close()


class Torrent(object):
    def __init__(self, handle, magnet_id):
        self.id = magnet_id
        self.info = handle.get_torrent_info()
        self._files = self.info.files()
        self.files = [TorrentInnerFile(f) for f in self._files]
        self.name = self.info.name()
        self.comment = self.info.comment()
        self.size = self.info.total_size()

    def __iter__(self):
        for file in self.files:
            yield file

    def to_dict(self):
        return {'id': self.id,
                'files': [inner_file.to_dict() for inner_file in self.files],
                'name': self.name,
                'comment': self.comment,
                'size': self.size}

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

    def to_dict(self):
        return self.__dict__

    @property
    def size_pretty(self):
        return pretty_size(self.size)

    def __repr__(self):
        return "<{name} - size : {size}>".format(name=self.name,
                                                 size=self.size_pretty)
