from sim.network import NoisyModel
from sim.node import DeadNode

from itertools import combinations


# === helpers ===


def common_sequence(network):
    """ Find the longest committed sequence common to 2f+1 nodes. """
    nodes = network.nodes.values()
    nodes_combinations = combinations(nodes, network.quorum)
    common = set()
    for c in nodes_combinations:
        db = [n.storage for n in c]
        seq = [x.committed if hasattr(x, 'committed') else set() for x in db]
        inter = set.intersection(*seq)
        common = inter if len(inter) > len(common) else common
    return common

def print_out(network):
    network.print_trace()
    print()
    network.nodes[3].log.print_out()
    [print(f'\n{n.storage}') for n in network.nodes.values()]
    print(f'{network.nodes[3].sync_storage}\n')
    print(f'Common committed sequence:\n{common_sequence(network)}')


# === simulations ===


def test_happy(network_and_environement):
    network, _ = network_and_environement
    network.run()
    print_out(network)
    assert len(common_sequence(network)) > 1


def test_dead_node(network_and_environement):
    network, _ = network_and_environement
    network.nodes[0] = DeadNode(0, network)
    network.run(until=100)
    print_out(network)
    assert len(common_sequence(network)) > 1


def test_noisy(network_and_environement):
    network, _ = network_and_environement
    network.model = NoisyModel()
    network.run(until=100)
    print_out(network)
    assert len(common_sequence(network)) > 1

