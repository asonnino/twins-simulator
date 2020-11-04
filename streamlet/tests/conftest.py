from sim.network import Network, SimpleModel
from streamlet.messages import Block, Vote
from streamlet.node import StreamletNode
from streamlet.storage import NodeStorage

import pytest
from unittest.mock import MagicMock
import simpy


@pytest.fixture
def genesis():
    return NodeStorage.make_genesis()


@pytest.fixture
def block(genesis):
    return Block(0, 1, genesis)


@pytest.fixture
def vote(block):
    return Vote(0, block)


@pytest.fixture
def three_votes(block):
    return [Vote(i, block) for i in range(3)]


@pytest.fixture
def network():
    net = Network(MagicMock(), MagicMock())
    [net.add_node(StreamletNode(i, network)) for i in range(4)]
    return net


@pytest.fixture
def storage():
    net = MagicMock(spec=Network)
    net.quorum = 3
    node = StreamletNode(0, net)
    return NodeStorage(node)


@pytest.fixture
def network_and_environement():
    env = simpy.Environment()
    network = Network(env, SimpleModel())
    nodes = [StreamletNode(i, network) for i in range(4)]
    [network.add_node(n) for n in nodes]
    return network, env
