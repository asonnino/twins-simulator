from sim.network import Network
from sim.leader_election import LeaderElection


class TwinsNetwork(Network):
    def __init__(self, env, model, round_partitions, firewall, num_of_twins):
        super().__init__(env, model)
        self.round_partitions = round_partitions
        self.firewall = firewall
        self.num_of_twins = num_of_twins

    @property
    def quorum(self):
        sole_nodes = len(self.nodes) - self.num_of_twins
        f = (sole_nodes - 1) // 3
        return sole_nodes - f

    def send(self, fromx, tox, message):
        if str(fromx.round) in self.round_partitions:
            partitions = self.round_partitions[str(fromx.round)]
            ok = any(tox.name in p and fromx.name in p for p in partitions)
            ok &= self._pass_firewall(fromx, tox)
            if ok:
                self.env.process(self._send(fromx, tox, message))

    def _pass_firewall(self, fromx, tox):
        ok = True
        if str(fromx.round) in self.firewall:
            rule = self.firewall[str(fromx.round)]
            if str(fromx.name) in rule:
                ok &= not tox.name in rule[str(fromx.name)]
        return ok


class TwinsLE(LeaderElection):
    def __init__(self, node, network, round_leaders):
        super().__init__(node, network)
        self.round_leaders = round_leaders

    def get_leader(self, round=None):
        round = self.node.round if round is None else round
        if str(round) in self.round_leaders:
            return self.round_leaders[str(round)]
        else:
            return []
