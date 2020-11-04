from sim.node import Node
from sim.network import BColors
from fhs.messages import Message, Block, GenericVote, Vote, NewView
from fhs.storage import NodeStorage, SyncStorage


class FHSNode(Node):
    DELAY = 10  # Max delay before timeout.

    def __init__(self, name, network, sync_storage):
        super().__init__(name, network)
        self.timeout = self.DELAY
        self.round = 2
        self.last_voted_round = 2
        self.preferred_round = 1

        qc2 = SyncStorage.make_genesis(network)[-1]
        self.highest_qc, self.highest_qc_round = qc2, 2

        # Block store (global for all nodes).
        self.sync_storage = sync_storage

        # Node store (each node has its own).
        self.node_storage = NodeStorage(self)

    def receive(self, message):
        """ Handles incoming messages. """

        if not isinstance(message, Message):
            assert False  # pragma: no cover

        if not message.verify(self.network):
            self.log(
                f'Received invalid message: {message}',
                color=BColors.WARNING
            )
            return

        # Handle incoming blocks.
        # Block message contains the previous QC: we handle separatly
        # the qc and the block itself (as they could be different messages).
        # The qc can be an instance of either QC or AggQC.
        if isinstance(message, Block):
            self.sync_storage.add_block(message)

            # Get the 3 ancestors of the block as follows:
            # b0 <- b1 <- b2 <- message
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
                self.node_storage.committed += [b0]

            # Check if we can vote for the new block.
            check = message.author in self.le.get_leader()
            check &= message.round > self.last_voted_round
            check &= b2.round >= self.preferred_round
            if check:
                self.timeout = self.DELAY
                self.last_voted_round = message.round
                vote = Vote(message.digest(), self.name)
                next_leader_idx = self.le.get_leader(round=self.round+1)
                next_leader = self.network.nodes[next_leader_idx]
                self.network.send(self, next_leader, vote)

        # Handle incoming votes and new view messages.
        elif isinstance(message, GenericVote):
            qc = self.node_storage.add_vote(message)
            if qc is not None:
                block = Block(qc, self.round+1, self.name)
                self.network.broadcast(self, block)

        else:
            assert False  # pragma: no cover

    def send(self):
        """ Main loop triggering timeouts. """

        # Send the very first block.
        if self.name in self.le.get_leader():
            block = Block(self.highest_qc, self.round+1, self.name)
            self.network.broadcast(self, block)

        # Trigger timeouts when necessary.
        while True:
            yield self.network.env.timeout(1)
            self.timeout -= 1
            if self.timeout == 0:
                self.timeout = self.DELAY
                vote = NewView(self.highest_qc, self.round, self.name)
                next_leader_idx = self.le.get_leader(round=self.round+1)
                next_leader = self.network.nodes[next_leader_idx]
                self.network.send(self, next_leader, vote)
