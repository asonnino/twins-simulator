from sim.node import Node
from sim.network import BColors
from fhs.messages import Message, Block, GenericVote, Vote, NewView
from fhs.storage import NodeStorage, SyncStorage


class FHSNode(Node):
    DELAY = 15  # Delay before timeout.

    def __init__(self, name, network, sync_storage):
        super().__init__(name, network)
        self.timeout = self.DELAY
        self.round = 3
        self.last_voted_round = 2
        self.preferred_round = 1

        qc2 = SyncStorage.make_genesis()[-1]
        self.highest_qc, self.highest_qc_round = qc2, 2

        # Block store (global for all nodes).
        self.sync_storage = sync_storage

        # Node store (each node has its own).
        self.storage = NodeStorage(self)

    def receive(self, message):
        """ Handles incoming messages. """

        if not (isinstance(message, Message) and message.verify(self.network)):
            assert False  # pragma: no cover

        # Handle incoming blocks.
        if isinstance(message, Block):
            self.sync_storage.add_block(message)
            self._process_qc(message.qc)
            self._process_block(message)

        # Handle incoming votes and new view messages.
        elif isinstance(message, GenericVote):
            qc = self.storage.add_vote(message)
            if qc is not None:
                self._process_block(qc.block(self.sync_storage))
                self._process_qc(qc)
                block = Block(qc, self.round, self.name)
                self.network.broadcast(self, block)

        else:
            assert False  # pragma: no cover

    def _process_block(self, block):
        prev_block = block.qc.block(self.sync_storage)

        # Check if we can vote for the block.
        check = block.author in self.le.get_leader()
        check &= block.round > self.last_voted_round
        check &= prev_block.round >= self.preferred_round
        if check:
            self.timeout = self.DELAY
            self.last_voted_round = block.round
            self.round = max(self.round, block.round+1)
            vote = Vote(block.digest(), self.name)
            indeces = self.le.get_leader(round=block.round+1)
            next_leaders = [self.network.nodes[x] for x in indeces]
            self.log(f'Sending vote {vote} to {next_leaders}')
            [self.network.send(self, x, vote) for x in next_leaders]

    def _process_qc(self, qc):
        self.log(f'Received QC {qc}', color=BColors.OK)

        # Get the 2 ancestors of the block as follows:
        # b0 <- b1 <- message
        b1 = qc.block(self.sync_storage)
        b0 = b1.qc.block(self.sync_storage)

        # Update the preferred round.
        self.preferred_round = max(self.preferred_round, b1.round)

        # Update the highest QC.
        if b1.round > self.highest_qc_round:
            self.highest_qc = qc
            self.highest_qc_round = b1.round

        # Update the committed sequence.
        self.storage.commit(b0)
        self.log(f'Committing {b0}', color=BColors.OK)

    def send(self):
        """ Main loop triggering timeouts. """

        # Send the very first block.
        if self.name in self.le.get_leader():
            block = Block(self.highest_qc, self.round, self.name)
            self.network.broadcast(self, block)

        # Trigger timeouts when necessary.
        while True:
            yield self.network.env.timeout(1)
            self.timeout -= 1
            if self.timeout == 0:
                self.log(
                    f'Timing out! (round {self.round})', color=BColors.WARNING
                )
                self.round += 1
                self.timeout = self.DELAY
                vote = NewView(self.highest_qc, self.round, self.name)
                indeces = self.le.get_leader()
                next_leaders = [self.network.nodes[x] for x in indeces]
                [self.network.send(self, x, vote) for x in next_leaders]
                self.log(f'Sending new view {vote} to {next_leaders}')
