from sim.node import Node, Logger
from fhs.messages import Message, Block, Vote
from fhs.storage import NodeStorage


class FHSNode(Node):
    def __init__(self, index, network):
        super().__init__(index, network)
        self.storage = NodeStorage(self)
        self.view = 0

    def receive(self, message):
        """ Process received message.

        Args:
            message (Message): The incoming message
        """
        if isinstance(message, Message) and message.verify(self.network):

            # Handle incoming blocks.
            if isinstance(message, Block):
                if not self.storage.contains(message):

                    # 1. Add it to storage.
                    self.storage.add_block(message)

                    # 2. Decide whether to vote on the block.
                    if self._can_vote(message):
                        vote = Vote(hash(message), self.view, self.index)
                        self.network.send(self, message.author, vote)

            # Handle incoming votes.
            elif isinstance(message, Vote):
                if not message.hash in self.storage.votes:
                    self.network.broadcast(self, message)
                self.storage.add_vote(message)

            else:
                assert False  # pragma: no cover

        else:
            assert False  # pragma: no cover

    def send(self):
        while True:
            self.round += 1
            self.log(f'Move to round {self.round}.')

            if self.index in self.le.get_leader():
                self.log('I am the leader.')
                chain = self.storage.get_longest_chains()[0]
                tip = chain[0]
                block = Block(self.name, self.round, tip)
                self.log(f'Broadcasting new block: {block}')
                self.network.broadcast(self, block)

            yield self.network.env.timeout(10)


    def _can_vote(self, block):
        return True # TODO
