class LeaderElection:
    def __init__(self, node, network):
        self.node = node
        self.network = network

    def get_leader(self):
        raise NotImplementedError  # pragma: no cover


class RoundRobinLE(LeaderElection):
    def get_leader(self, round=None):
        nodes = list(self.network.nodes.values())
        nodes.sort(key=lambda n: n.index)
        round = self.node.round if round is None else round
        return [nodes[round % len(nodes)].index]
