import zmq

from torrentsearcher import constants
from torrentsearcher.torrent_client.torrent_info import TorrentResolveMsg

__author__ = 'Omer'


class TorrentResolverMixin(object):
    SEND_ADDR = constants.TORRENTS_IN_STREAM
    RECV_ADDR = constants.TORRENTS_OUT_STREAM

    def __init__(self):
        self.context = zmq.Context.instance()
        self.recv_sock = self.context.socket(zmq.PULL)
        self.send_sock = self.context.socket(zmq.PUSH)
        self.send_sock.connect(self.SEND_ADDR)
        self.recv_sock.connect(self.RECV_ADDR)

    def send_resolve_magnet_message(self, magnet_link, timeout=30):
        msg = TorrentResolveMsg(magnet_link=magnet_link, timeout=timeout)
        msg.send_msg(self.send_sock)
