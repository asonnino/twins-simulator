from streamlet.messages import Block, Vote


def test_add_block(storage, block):
    assert not storage.pending
    storage.add_block(block)
    assert storage.pending == {hash(block): block}
    assert not hash(block) in storage.delivered


def test_add_vote(storage, vote):
    assert not storage.votes
    storage.add_vote(vote)
    assert vote.hash in storage.votes


def test_deliver(storage, block, three_votes, genesis):
    storage.add_block(block)
    assert storage.pending
    assert not hash(block) in storage.delivered
    [storage.add_vote(v) for v in three_votes]
    assert not storage.pending
    assert hash(block) in storage.delivered


def test_contains(storage, block):
    assert not storage.contains(block)

    storage.add_block(block)
    assert storage.contains(block)

    missing = Block('Node0', 2, block)
    assert not storage.contains(missing)


def test_get_longest_chains(storage, block, three_votes, genesis):
    storage.add_block(block)
    [storage.add_vote(v) for v in three_votes]
    assert storage.get_longest_chains() == [[block, genesis]]


def test_get_longest_chains_new_longest(storage, genesis):
    block1 = Block('Node0', 1, genesis)
    votes1 = [Vote(f'Node{i}', block1) for i in range(3)]
    storage.add_block(block1)
    [storage.add_vote(v) for v in votes1]

    block2 = Block('Node0', 2, block1)
    votes2 = [Vote(f'Node{i}', block2) for i in range(3)]
    storage.add_block(block2)
    [storage.add_vote(v) for v in votes2]
    assert len(storage.get_longest_chains()) == 1
    assert len(storage.get_longest_chains()[0]) == 3


def test_get_longest_chains_two_longest(storage, genesis):
    block1a = Block('Node0', 1, genesis)
    votes1a = [Vote(f'Node{i}', block1a) for i in range(3)]
    storage.add_block(block1a)
    [storage.add_vote(v) for v in votes1a]

    block1b = Block('Node1', 1, genesis)
    votes1b = [Vote(f'Node{i}', block1b) for i in range(3)]
    storage.add_block(block1b)
    [storage.add_vote(v) for v in votes1b]
    assert len(storage.get_longest_chains()) == 2


def test_get_longest_chains_incomplete(storage, block, genesis):
    block2 = Block('Node0', 2, block)
    votes2 = [Vote(f'Node{i}', block2) for i in range(3)]
    storage.add_block(block2)
    [storage.add_vote(v) for v in votes2]
    assert storage.get_longest_chains() == [[genesis]]
