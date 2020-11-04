from sim.network import NoisyModel
from sim.node import DeadNode


# === helpers ===


def common_sequence(network):
    pass  # TODO


def print_out(network):
    network.print_trace()
    print()
    network.nodes[3].log.print_out()
    print()
    [print(n.storage) for n in network.nodes.values()]
    print()
    print(network.nodes[3].sync_storage)


# === simulations ===


def test_happy(network_and_environement):
    network, _ = network_and_environement
    network.run()
    print_out(network)


def test_dead_node(network_and_environement):
    network, _ = network_and_environement
    network.nodes[0] = DeadNode(0, network)
    network.run(until=100)
    print_out(network)


def test_noisy(network_and_environement):
    network, _ = network_and_environement
    network.model = NoisyModel()
    network.run(until=100)
    print_out(network)

