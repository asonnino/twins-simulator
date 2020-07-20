from sim.network import Network
from sim.leader_election import LeaderElection


class TwinsNetwork(Network):
    def __init__(self, env, model, round_partitions, num_of_twins):
        super().__init__(env, model)
        self.round_partitions = round_partitions
        self.num_of_twins = num_of_twins

    @property
    def quorum(self):
        sole_nodes = len(self.nodes) - self.num_of_twins
        f = (sole_nodes - 1) // 3
        return sole_nodes - f

    def send(self, fromx, tox, message):
        if str(fromx.round) in self.round_partitions:
            partitions = self.round_partitions[str(fromx.round)]
            if any(tox.index in p and fromx.index in p for p in partitions):
                self.env.process(self._send(fromx, tox, message))


class TwinsLE(LeaderElection):
    def __init__(self, node, network, round_leaders):
        super().__init__(node, network)
        self.round_leaders = round_leaders

    def get_leader(self):
        if str(self.node.round) in self.round_leaders:
            return self.round_leaders[str(self.node.round)]
        else:
            return []
