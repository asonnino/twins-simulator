class LeaderElection:
    def __init__(self, node, network):
        self.node = node
        self.network = network

    def get_leader(self):
        raise NotImplementedError  # pragma: no cover


class RoundRobinLE(LeaderElection):
    def get_leader(self):
        nodes = list(self.network.nodes.values())
        nodes.sort(key=lambda n: n.index)
        return [nodes[self.node.round % len(nodes)].index]
