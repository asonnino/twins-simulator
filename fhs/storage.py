from sim.network import BColors
from fhs.messages import Block, Vote, NewView, QC, AggQC

from collections import defaultdict


class NodeStorage():
    """ The node storage instance. """

    def __init__(self, node):
        self.node = node
        genesis = NodeStorage.make_genesis(self.node.network)
        b0, _, b1, _, b2, _ = genesis
        self.blocks = {x.digest(): x for x in [b0, b1, b2]}
        self.committed = []
        self.votes = defaultdict(set)
        self.new_views = {}
        
    def __repr__(self):
        return (
            f'Storage content ({self.node} at round {self.node.view}):\n'
            f'\tBlocks({len(self.blocks)}): {self.blocks}\n'
            f'\tVotes({len(self.votes)}): {self.votes}\n'
            f'\tNewViews({len(self.new_views)}): {self.new_views}\n'
        )

    @staticmethod
    def make_genesis(network):
        b0 = Block('Genesis', 0, None)
        qc0 = QC({Vote(b0.digest(), x) for x in network.nodes.keys()})
        b1 = Block(qc0, 1, None)
        qc1 = QC({Vote(b1.digest(), x) for x in network.nodes.keys()})
        b2 = Block(qc1, 2, None)
        qc2 = QC({Vote(b2.digest(), x) for x in network.nodes.keys()})
        return b0, qc0, b1, qc1, b2, qc2

    def add_block(self, block):
        self.blocks[block.digest()] = block

    def add_vote(self, message):
        if isinstance(message, Vote):
            digest = message.block_hash
            votes = self._can_make_qc(self.votes, digest, message)
            return QC(votes) if votes is not None else None

        elif isinstance(message, NewView):
            round = message.round
            new_views = self._can_make_qc(self.new_views, round, message)
            return AggQC(new_views) if new_views is not None else None

        else:
            assert False  # pragma: no cover
        
    def _can_make_qc(self, collection, key, value):
        before = len(collection[key]) >= self.node.network.quorum
        collection[key].add(value)
        after = len(collection[key]) >= self.node.network.quorum
        return collection[key] if (after and not before) else None