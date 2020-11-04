from sim.network import Network, SimpleModel
from fhs.node import FHSNode
from fhs.storage import SyncStorage

import pytest
import simpy


@pytest.fixture
def network_and_environement():
    env = simpy.Environment()
    network = Network(env, SimpleModel())

    genesis = SyncStorage.make_genesis()
    sync_storage = SyncStorage(genesis)
    nodes = [FHSNode(i, network, sync_storage) for i in range(4)]
    [network.add_node(n) for n in nodes]
    return network, env
