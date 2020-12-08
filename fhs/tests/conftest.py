from sim.network import Network, SimpleModel
from fhs.node import FHSNode
from fhs.storage import SyncStorage

import pytest
import simpy


@pytest.fixture
def network_and_environement():
    env = simpy.Environment()
    network = Network(env, SimpleModel())
    global_store = SyncStorage()
    nodes = [FHSNode(i, network, global_store) for i in range(4)]
    [network.add_node(n) for n in nodes]
    return network, env
