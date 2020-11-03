from sim.node import Node
from sim.network import BColors
from fhs.messages import Message, Block, GenericVote, Vote, NewView
from fhs.storage import NodeStorage

# TODO: Fix nodes to use indeces instead of names.
# And rename index -> name.

class FHSNode(Node):
    def __init__(self, index, network):
        super().__init__(index, network)
        self.round = 2

        # Global store simulating sync requests.
        self.storage = NodeStorage(self)  
        
        self.last_voted_round = 2
        self.preferred_round = 1

        qc2 = NodeStorage.make_genesis(network)[-1]
        self.highest_qc, self.highest_qc_round = qc2, 2

    def receive(self, message):
        if not isinstance(message, Message):
            assert False  # pragma: no cover

        if not message.verify(self.network):
            self.log(
                f'Received invalid message: {message}', 
                color=BColors.WARNING
            )
            return

        # Handle incoming blocks.
        if isinstance(message, Block):
            self.storage.add_block(message)

            b2 = message.qc.block(self.storage)
            b1 = b2.qc.block(self.storage)
            b0 = b1.qc.block(self.storage)

            # Update the current round.
            self.round = max(self.round, b2.round+1)

            # Update the preferred round.
            self.preferred_round = max(self.preferred_round, b1.round)
            
            # Update the highest QC.
            if b2.round > self.highest_qc_round:
                self.highest_qc = message.qc
                self.highest_qc_round = b2.round

            # Update the committed sequence.
            check = b1.round == b0.round + 1
            check &= b2.round == b1.round + 1
            if check:
                self.storage.committed += [b0]

            # Check if we can vote for the new block.
            check = message.author in self.le.get_leader()
            check &= message.round > self.last_voted_round
            check &= b2.round >= self.preferred_round
            if check:
                self.last_voted_round = message.round
                vote = Vote(message.digest(), self.index)
                next_leader_idx = self.le.get_leader(round=self.round+1)
                next_leader = self.network.nodes[next_leader_idx]
                self.network.send(self, next_leader, vote)

        # Handle incoming votes and new view messages.
        elif isinstance(message, GenericVote):
            qc = self.storage.add_vote(message)
            if qc is not None:
                block = Block(qc, self.round+1, self.index)
                self.network.broadcast(self, block)

        else:
            assert False  # pragma: no cover

    def send(self):
        if self.index in self.le.get_leader():
            block = Block(self.highest_qc, self.round+1, self.index)
            self.network.broadcast(self, block)

        while True:
            # TODO: send NewView message upon timeout.
            yield self.network.env.timeout(10)
