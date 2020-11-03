from sim.message import Message


class Block(Message):
    def __init__(self, qc, view, author, payload='*'*250):
        self.qc = qc
        self.view = view
        self.author = author
        self.payload = payload
        self.signature = True

    def size(self):
        return self.qc.size() + 64 + 32 + len(self.commands) + 64

    def verify(self):
        return self.signature and self.qc.verify()

    def __hash__(self):
        return self


class Vote(Message):
    def __init__(block_hash, view, author):
        self.block_hash = block_hash
        self.view = view
        self.author = author
        self.signature = True

    def size(self):
        return 32 + 64 + 32 + 64

    def verify(self):
        return self.signature


class QC(Message):
    def __init__(self, block_hash, votes):
        self.block_hash = block_hash
        self.votes = votes

    def size(self):
        return 32 + 32

    def verify(self):
        return all(x.verify() for x in self.votes)


class NewView(Message):
    def __init__(self, qc, view, author):
        self.qc = qc
        self.view = view
        self.author = author
        self.signature = True

    def size(self):
        return  self.qc.size() + 64 + 32 + 64

    def verify(self):
        return self.signature and self.qc.verify()


class AggQC(Message):
    def __init__(self, new_views):
        self.new_views = new_views

    def size(self):
        return sum(x.size() for x in self.new_views) + 32

    def verify(self):
        return all(x.verify() for x in self.new_views)
