from sim.network import BColors
from sim.message import Message
from sim.leader_election import RoundRobinLE


class Node():
    def __init__(self, name, network):
        self.name = name
        self.network = network
        self.round = 0
        self.log = Logger()
        self.le = RoundRobinLE(self, self.network)
        self.storage = dict()

    def __repr__(self):
        return f'Node{self.name}'

    def set_le(self, le):
        self.le = le

    def receive(self, message):
        """ Process received message.

        Args:
            message (Message): The incoming message
        """
        if isinstance(message, Message) and message.verify(self.network):
            raise NotImplementedError

    def send(self):
        raise NotImplementedError


class Logger():
    def __init__(self):
        self.log = []

    def __call__(self, msg, color=None):
        msg = msg if color is None else f'{color}{msg}{BColors.ENDC}'
        self.log.append(msg)

    def print_out(self):
        [print(line) for line in self.log]


class DeadNode(Node):
    def receive(self, message):
        return

    def send(self):
        while True:
            yield self.network.env.timeout(10)
