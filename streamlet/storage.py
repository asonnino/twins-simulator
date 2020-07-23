from sim.network import BColors
from streamlet.messages import Block, Vote

from collections import defaultdict


class NodeStorage():
    """ The node storage instance. """

    def __init__(self, node):
        """ Initialize the storage.

        Args:
            node (Node): The node.
        """
        self.node = node
        self.pending = dict()
        self.votes = defaultdict(set)
        genesis = NodeStorage.make_genesis()
        self.delivered = {hash(genesis): genesis}

    def __repr__(self):
        return (
            f'Storage content ({self.node} at round {self.node.round}):\n'
            f'\tPending({len(self.pending)}): {self.pending}\n'
            f'\tDelivered({len(self.delivered)}): {self.delivered}\n'
            f'\tVotes({len(self.votes)}): {self.votes}\n'
            f'\tLongest Chain(s): {self.get_longest_chains()}\n'
        )

    @staticmethod
    def make_genesis():
        """ Make genesis blocks.

        Returns:
            Block: A genesis block.
        """
        return Block('Genesis', 0, 0)

    def contains(self, block):
        """ Check if we already have a block for this (leader, round) label.

        Args:
            block (Block): The block to check.

        Returns:
            bool: Whether this (leader, round) label is new.
        """
        storage = {**self.delivered, **self.pending}
        for b in storage.values():
            if block.round == b.round and block.author == b.author:
                return True
        return False

    def add_block(self, block):
        """ Add valid block to the storage and try to deliver the voted block.

        Note that votes may arrive before the block.

        Args:
            block (Block): A block.
        """
        digest = hash(block)
        self.pending[digest] = block
        self._try_deliver(digest)

    def add_vote(self, vote):
        """ Add valid vote to the storage and try to deliver the voted block.

        Args:
            block (Vote): A vote.
        """
        digest = vote.hash
        self.votes[digest].add(vote)
        self._try_deliver(digest)

    def _try_deliver(self, digest):
        if len(self.votes[digest]) >= self.node.network.quorum:
            if digest in self.pending:
                block = self.pending.pop(digest)
                self.delivered[digest] = block
                self.node.log(f'Delivered block: {block}', color=BColors.OK)

    def get_longest_chains(self):
        """ Inefficient way to find the longest chain(s).

        The chains are ordered, the tail is in position 0, and the genesis
        in position [-1].

        Returns:
            list: The longest chain(s).
        """
        longests = [[]]
        for block in self.delivered.values():
            chain = self._get_chain(block, [])
            if len(chain) == len(longests[0]):
                longests.append(chain)
            elif len(chain) > len(longests[0]):
                longests.clear()
                longests.append(chain)
        assert len(longests) > 0 and len(longests[0]) > 0
        return longests

    def _get_chain(self, block, chain):
        if block.link == 0:  # We reached the genesis
            return chain + [block]
        elif block.link not in self.delivered:  # Incomplete chain, discard
            return []
        else:
            chain += [block]
            return self._get_chain(self.delivered[block.link], chain)

    def get_finalized_blocks(self):
        chain = self.get_longest_chains()[0] # Select any chain
        if len(chain) < 3:
            return []

        consecutives_rounds = 1
        last_round = chain[0].round
        for i, block in enumerate(chain[1:]):
            if block.round + 1 == last_round:
                consecutives_rounds += 1
                last_round = block.round
            else:
                consecutives_rounds = 1

            if consecutives_rounds == 3:
                return chain[i:]

        return []
