import time
import simplejson as json

import pytest
import zmq
from torrentsearcher import constants
from zmq.eventloop import IOLoop


from torrentsearcher.utils.torrent_info import TorrentClient, TorrentResolveMsg

sample_magnet_link = 'magnet:?xt=urn:btih:1a56b539a9030efdaf9864c50303b546ac8dc0ce&dn=Ayreon+-+2013+-+The+Theory+of+Everything+320kbps&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'


context = zmq.Context.instance()


# send_sock = context.socket(zmq.PUSH)
# recv_sock = context.socket(zmq.PULL)
# commands_sock = context.socket(zmq.PUSH)

# send_sock.connect('tcp://localhost:5555')
# recv_sock.connect('tcp://localhost:5556')
# commands_sock.connect('tcp://localhost:5557')

@pytest.yield_fixture
def zmqcontext():
    context = zmq.Context()
    yield context
    context.term()


@pytest.yield_fixture
def torrent_client(zmqcontext):
    client = TorrentClient(ctx=zmqcontext, loop=IOLoop())
    client.start()
    yield client
    client.stop()


@pytest.yield_fixture
def torrent_producer(zmqcontext):
    send_sock = zmqcontext.socket(zmq.PUSH)
    recv_sock = zmqcontext.socket(zmq.PULL)
    send_sock.connect(constants.TORRENTS_IN_STREAM)
    recv_sock.connect(constants.TORRENTS_OUT_STREAM)
    yield (send_sock, recv_sock)
    send_sock.close()
    recv_sock.close()


@pytest.fixture
def torrent_resolve_message():
    return TorrentResolveMsg(magnet_link=sample_magnet_link, timeout=30)


def test_client_receives_message(torrent_client, torrent_producer, torrent_resolve_message):
    send, recv = torrent_producer
    torrent_resolve_message.send_msg(send)
    time.sleep(1)
    assert len(torrent_client.tasks) == 1


def test_client_receives_and_resolves_message(torrent_client, torrent_producer, torrent_resolve_message):
    send, recv = torrent_producer
    torrent_resolve_message.send_msg(send)
    response = None
    start_time = time.time()
    while not response:
        result = recv.recv_json()
        response = json.loads(result['object'])

    assert response is not None


def test_client_receives_and_resolves_messages(torrent_client, torrent_producer, torrent_resolve_message):
    send, recv = torrent_producer
    torrent_resolve_message.send_msg(send)
    response = None
    start_time = time.time()
    while not response:
        result = recv.recv_json()
        response = json.loads(result['object'])

    assert response is not None
