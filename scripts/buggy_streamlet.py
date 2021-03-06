'''
This is a quick and dirty simulation of a buggy stremalet protocol, as
described in the Twins paper.
'''
import sys
sys.path += '../streamlet'

import logging
from collections import defaultdict
from json import load
from streamlet.messages import Block


class Blockchain:
    def __init__(self, nodes):
        genesis = Block('Genesis', 0, 0)
        self.voted = {n: defaultdict(int) for n in nodes}
        self.last_notarized = {n: genesis for n in nodes}
        self.last_voted = {n: genesis for n in nodes}
        self.notarized = {n: {0: genesis} for n in nodes}

    def clear(self):
        nodes = [k for k in self.last_notarized.keys()]
        self.__init__(nodes)

    def get_finalized(self, node):
        blocks = list(self.notarized[node].values())
        blocks.sort(key=lambda b: b.round, reverse=True)
        for i, block in enumerate(blocks):
            r = block.round
            if r-1 in self.notarized[node] and r-2 in self.notarized[node]:
                assert len(blocks) > i+1
                return blocks[i+1:]

class Network:
    def __init__(self, num_of_nodes, num_of_twins):
        self.num_of_nodes = num_of_nodes
        self.num_of_twins = num_of_twins
        self.nodes = [i for i in range(self.num_of_nodes+self.num_of_twins)]
        self.chain = Blockchain(self.nodes)

    def quorum(self):
        f = (self.num_of_nodes - 1) // 3
        return self.num_of_nodes - f

    def same_partition(self, node1, node2, partitions):
        return any(node1 in p and node2 in p for p in partitions)


    def run(self, num_of_rounds, twins_leaders, twins_partitions):
        for r in range(1, num_of_rounds+1):
            logging.debug(f'Entering round: {r}')

            for leader in twins_leaders[str(r)]:
                # Propose block.
                tail_block = self.chain.last_notarized[leader]
                block = Block(f'Node{leader}', r, tail_block)
                logging.debug(f'Node {leader} proposes {block}')

                # Vote for the block.
                # We introduce a bug in the voting condition: instead of
                # comparing the block heights we compare their round number.
                partitions = twins_partitions[str(r)]
                for voter in self.nodes:
                    last_notarized = self.chain.last_notarized[voter]
                    can_vote = self.same_partition(leader, voter, partitions)
                    can_vote &= last_notarized.round <= tail_block.round
                    if can_vote:
                        self.chain.last_voted[voter] = block
                        logging.debug(f'Node {voter} votes for {block}')
                        for node in self.nodes:
                            if self.same_partition(node, voter, partitions):
                                self.chain.voted[node][hash(block)] += 1

                # Update notarized / finalized.
                for voter in self.nodes:
                    if self.chain.voted[voter][hash(block)] >= self.quorum():
                        self.chain.last_notarized[voter] = block
                        self.chain.notarized[voter][r] = block
                        logging.debug(f'Node {voter} notarizes {block}')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG, format='[%(levelname)s] %(message)s'
    )

    assert len(sys.argv) > 1
    with open(sys.argv[1]) as f:
        data = load(f)

    num_of_nodes = data['num_of_nodes']
    num_of_twins = data['num_of_twins']

    network = Network(num_of_nodes, num_of_twins)
    scenarios = data['scenarios']
    for i, scenario in enumerate(scenarios):
        network.chain.clear()
        logging.info(f'Scenario {i+1}/{len(scenarios)}')

        twins_leaders = scenario['round_leaders']
        twins_partitions = scenario['round_partitions']
        num_of_rounds = len(twins_partitions)
        logging.info(f'Running {num_of_rounds} rounds.')
        network.run(num_of_rounds, twins_leaders, twins_partitions)

        logging.info('Last notarized block:')
        for node, block in network.chain.last_notarized.items():
            logging.info(f'Node{node}: {block}')
        logging.info('Finalized block(s):')
        for node in network.nodes:
            logging.info(f'Node{node}: {network.chain.get_finalized(node)}')
