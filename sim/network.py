import numpy as np


class BColors:
    OK = '\033[92m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'


class Network:
    def __init__(self, env, model):
        self.nodes = dict()
        self.env = env
        self.trace = []
        self.model = model

    @property
    def quorum(self):
        f = (len(self.nodes) - 1) // 3
        return len(self.nodes) - f

    def add_node(self, node):
        self.nodes[node.name] = node

    def run(self, until=50):
        assert len(self.nodes) > 0  # Don't forget to add nodes.
        [self.env.process(n.send()) for n in self.nodes.values()]
        self.env.run(until=until)

    def broadcast(self, fromx, message):
        for tox in self.nodes.values():
            self.send(fromx, tox, message)

    def send(self, fromx, tox, message):
        self.env.process(self._send(fromx, tox, message))

    def _send(self, fromx, tox, message):
        # Only start sending after a delay.
        delay = 0.0 if fromx == tox else self.model.delay(fromx, tox, message)
        sent_time = round(self.env.now, 2)
        yield self.env.timeout(delay)

        # Record a trace.
        entry = (
            f'{sent_time:.2f}',  # send time
            f'{round(self.env.now, 2):.2f}',  # receiving time
            fromx,  # sender
            tox,  # receiver
            message  # message
        )
        self.trace.append(entry)
        tox.log(entry, color=BColors.INFO)

        # Deliver messages.
        tox.receive(message)

    def print_trace(self, filter=None):
        print()
        [print(t) for t in self.trace if filter is None or filter(t)]


class SimpleModel:
    """ Simple network delay.

    The delay is composed of three terms:
        - a constant term
        - a term linear in the size of the message
        - random noise from a gamma distribution
    """

    def __init__(self):
        self.constant = 1
        self.linear_factor = 1/1000
        self.gamma_k, self.gamma_theta = 2, 1

    def delay(self, fromx, tox, message):
        delay = self.constant
        delay += message.size() * self.linear_factor
        delay += np.random.gamma(self.gamma_k, self.gamma_theta)
        return delay


class NoisyModel(SimpleModel):
    def __init__(self):
        super().__init__()
        self.gamma_k, self.gamma_theta = 1, 4
