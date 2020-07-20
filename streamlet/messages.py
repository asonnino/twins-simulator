from sim.message import Message


class Block(Message):
    def __init__(self, author, round, link, payload='*'*250):
        self.author = author
        self.round = round
        self.link = hash(link)
        self.payload = payload
        self.signature = True

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and self.author == other.author \
            and self.round == other.round \
            and self.payload == other.payload \
            and self.link == other.link

    def __hash__(self):
        digest = hash(self.author)
        digest ^= hash(self.round) << 1
        digest ^= hash(self.payload) << 1
        digest ^= hash(self.link) << 1
        return digest

    def __repr__(self):
        data = str(self.payload)
        data = data if len(data) < 3 else f'{data[:1]}..'
        digest = hash(self)
        return f'[{digest}]BK({self.author}, {self.round}, {self.link}, {data})'

    def verify(self, network):
        return self.author in network.nodes.keys() and self.signature

    def size(self):
        return len(self.payload) * 8 + 32 + 128 + 16


class Vote(Message):
    def __init__(self, author, block):
        self.author = author
        self.hash = hash(block)
        self.signature = True

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and self.author == other.author \
            and self.hash == other.hash

    def __hash__(self):
        digest = hash(self.author)
        digest ^= hash(self.hash) << 1
        return digest

    def __repr__(self):
        return f'[{hash(self)}]V({self.author}, {self.hash})'

    def verify(self, network):
        return self.author in network.nodes.keys() and self.signature

    def size(self):
        return 32 + 128 + 16
