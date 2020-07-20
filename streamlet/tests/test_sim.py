from sim.network import NoisyModel
from sim.node import DeadNode

from itertools import combinations
import pytest


# === helpers ===


def highest_common_round(network):
    """ Find the highest round common to 2f+1 nodes. """
    nodes = network.nodes.values()
    nodes_combinations = combinations(nodes, network.quorum)
    common_round = 0
    for c in nodes_combinations:
        value = min([n.round for n in c])
        common_round = max(common_round, value)
    return common_round


def print_out(network):
    network.print_trace()
    network.nodes['Node3'].log.print_out()
    [print(n.storage) for n in network.nodes.values()]
    print(f'\nHigest common round: {highest_common_round(network)}\n')


# === simulations ===


def test_happy(network_and_environement):
    network, env = network_and_environement
    network.run()
    print_out(network)
    assert highest_common_round(network) > 0


def test_dead_node(network_and_environement):
    network, env = network_and_environement
    network.nodes['Node0'] = DeadNode(0, network)
    network.run()
    print_out(network)
    assert highest_common_round(network) > 0


def test_noisy(network_and_environement):
    network, env = network_and_environement
    network.model = NoisyModel()
    network.run()
    print_out(network)
    assert highest_common_round(network) > 0
