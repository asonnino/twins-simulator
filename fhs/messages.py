from sim.message import Message


class Block(Message):
    def __init__(self, qc, round, author, payload='*'*250):
        self.qc = qc
        self.round = round
        self.author = author
        self.payload = payload
        self.signature = True

    def size(self):
        return self.qc.size() + 64 + 32 + len(self.payload) + 64

    def verify(self, network):
        check = self.signature
        check &= self.author in network.nodes.keys()
        check &= self.qc.verify(network)
        return check

    def __repr__(self):
        data = self.payload[0]
        return f'BK(Node{self.author}, {self.round}, {self.qc}, {data})'

    def digest(self):
        return f'{self.author}||{self.round}'


# --- Votes ---


class GenericVote(Message):
    pass


class Vote(GenericVote):
    def __init__(self, block_hash, author):
        self.block_hash = block_hash
        self.author = author
        self.signature = True

    def size(self):
        return 32 + 32 + 64

    def verify(self, network):
        return self.signature and self.author in network.nodes.keys()

    def __repr__(self):
        return f'V(Node{self.author}, {self.block_hash})'


class NewView(GenericVote):
    def __init__(self, qc, round, author):
        self.qc = qc
        self.round = round
        self.author = author
        self.signature = True

    def size(self):
        return self.qc.size() + 64 + 32 + 64

    def verify(self, network):
        check = self.signature
        check &= self.author in network.nodes.keys()
        check &= self.qc.verify(network)
        return check

    def __repr__(self):
        return f'NV(Node{self.author}, {self.round}, {self.qc})'


# --- QCs ---


class GenericQC(Message):
    def block(self, storage):
        raise NotImplementedError  # pragma: no cover


class QC(GenericQC):
    def __init__(self, votes):
        assert votes
        self.votes = votes

    def size(self):
        return 32

    def verify(self, network):
        check = all(x.verify(network) for x in self.votes)
        check &= len({x.block_hash for x in self.votes}) == 1
        check &= len(self.votes) >= network.quorum
        return check

    def block(self, storage):
        block_hash = next(x.block_hash for x in self.votes)
        return storage.blocks[block_hash]

    def __repr__(self):
        return f'QC({next(iter(self.votes)).block_hash})'


class AggQC(GenericQC):
    def __init__(self, new_views):
        self.new_views = new_views

    def size(self):
        return sum(x.size() for x in self.new_views)

    def verify(self, network):
        check = all(x.verify(network) for x in self.new_views)
        check &= len(self.new_views) >= network.quorum
        return check

    def block(self, storage):
        qcs = [x.qc for x in self.new_views]
        blocks = [x.block(storage) for x in qcs]
        rounds = [x.round for x in blocks]
        return blocks[rounds.index(max(rounds))]

    def __repr__(self):
        return f'AggQC({[x.qc for x in self.new_views]})'
