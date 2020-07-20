from sim.node import Node, Logger
from streamlet.messages import Message, Block, Vote
from streamlet.storage import NodeStorage


class StreamletNode(Node):
    def __init__(self, index, network):
        super().__init__(index, network)
        self.storage = NodeStorage(self)

    def receive(self, message):
        """ Process received message.

        Args:
            message (Message): The incoming message
        """
        if isinstance(message, Message) and message.verify(self.network):

            # Handle incoming blocks.
            if isinstance(message, Block):
                if not self.storage.contains(message):

                    # 1. Re-braodcast the block and add it to storage.
                    self.network.broadcast(self, message)
                    self.storage.add_block(message)

                    # 2. Decide whether to vote on the block.
                    chains = self.storage.get_longest_chains()
                    tips = [c[0] for c in self.storage.get_longest_chains()]
                    hash_tips = [hash(b) for b in tips]
                    if message.link in hash_tips:
                        vote = Vote(self.name, message)
                        self.log(f'Broadcasting vote: {vote}')
                        self.network.broadcast(self, vote)

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
