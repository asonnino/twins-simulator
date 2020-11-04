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
        check &= self.qc.verify()
        return check

    def __repr__(self):
        data = str(self.payload)
        data = data if len(data) < 3 else f'{data[:1]}..'
        return f'BK({self.author}, {self.round}, {self.digest()}, {data})'

    def digest(self):
        return f'H({self.author}||{self.round})'


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
        return f'V({self.author}, {self.block_hash})'


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
        check &= self.qc.verify()
        return check

    def __repr__(self):
        return f'NV({self.author}, {self.round}, {self.qc})'


# --- QCs ---


class GenericQC(Message):
    def block(self, storage):
        raise NotImplementedError


class QC(GenericQC):
    def __init__(self, votes):
        self.votes = votes

    def size(self):
        return 32

    def verify(self, network):
        check = all(x.verify() for x in self.votes)
        check &= len({x.block_hash for x in self.votes}) == 1
        check &= len(self.votes) >= network.quorum
        return check

    def block(self, storage):
        block_hash = next(x.block_hash for x in self.votes)
        return storage.blocks[block_hash]

    def __repr__(self):
        return f'QC({self.votes[0].block_hash})'


class AggQC(GenericQC):
    def __init__(self, new_views):
        self.new_views = new_views

    def size(self):
        return sum(x.size() for x in self.new_views)

    def verify(self, network):
        check = all(x.verify() for x in self.new_views)
        check &= len(self.new_views) >= network.quorum
        return check

    def block(self, storage):
        qcs = [x.qc for x in self.new_views]
        blocks = [x.block(storage) for x in qcs]
        rounds = [x.round for x in blocks]
        return blocks.index(max(rounds))

    def __repr__(self):
        return f'AggQC(..)'
