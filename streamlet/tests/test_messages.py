from sim.network import Network
from streamlet.messages import Block, Vote


def test_block_eq(block, genesis):
    assert block == Block(0, 1, genesis)
    assert block != Block(0, 2, genesis)


def test_block_hash(block, genesis):
    assert hash(block) == hash(Block(0, 1, genesis))
    assert hash(block) != hash(Block('NodeX', 1, genesis))


def test_block_verify(block, network):
    assert block.verify(network)
    bad_block = Block('NodeX', 1, block)
    assert not bad_block.verify(network)


def test_vote_eq(vote, block):
    assert vote == Vote(0, block)
    assert vote != Vote('NodeX', block)


def test_vote_hash(vote, block):
    assert hash(vote) == hash(Vote(0, block))
    assert hash(vote) != hash(Vote('NodeX', block))


def test_vote_verify(vote, block, network):
    assert vote.verify(network)
    bad_vote = Vote('NodeX', block)
    assert not bad_vote.verify(network)
