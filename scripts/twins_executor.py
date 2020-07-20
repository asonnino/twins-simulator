import sys
sys.path += '../streamlet'
sys.path += '../twins'

from streamlet.node import StreamletNode
from sim.network import SimpleModel
from twins.twins import TwinsNetwork, TwinsLE

import logging
from json import load, dumps
import simpy
import argparse
from os.path import join


class TwinsRunner:
    def __init__(self, file_path, log_path=None, NodeClass=StreamletNode):
        self.file_path = file_path
        self.log_path = log_path
        self.NodeClass = NodeClass

        with open(file_path) as f:
            data = load(f)

        self.num_of_nodes = data['num_of_nodes']
        self.num_of_twins = data['num_of_twins']
        self.scenarios = data['scenarios']
        logging.debug(f'Scenario file {args.path} successfully loaded.')
        logging.info(
            f'Settings: {self.num_of_nodes} nodes, {self.num_of_twins} twins, '
            f'and {len(self.scenarios)} scenarios.'
        )

    def run(self):
        for i, scenario in enumerate(self.scenarios):
            logging.info(f'Running scenario {i+1}/{len(self.scenarios)}')
            network = runner._run_scenario(scenario)

            if self.log_path is not None:
                file_path = join(self.log_path, f'{self.file_path}-{i+1}.log')
                runner._print_log(file_path, scenario, network)
                logging.info(f'Log saved in {file_path}')

    def _run_scenario(self, scenario):
        logging.debug('1/3 Reading scenario.')
        round_leaders = scenario['round_leaders']
        round_partitions = scenario['round_partitions']

        logging.debug('2/3 Setting up network.')
        env = simpy.Environment()
        model = SimpleModel()
        network = TwinsNetwork(env, model, round_partitions, self.num_of_twins)

        nodes = [self.NodeClass(i, network) for i in range(self.num_of_nodes)]
        [n.set_le(TwinsLE(n, network, round_leaders)) for n in nodes]
        [network.add_node(n) for n in nodes]

        logging.debug(f'3/3 Executing scenario ({len(round_leaders)} rounds).')
        network.run()
        return network

    def _print_log(self, file_path, scenario, network):
        data = [f'Settings: {self.num_of_nodes} nodes, {self.num_of_twins} ']
        data += [f'twins, and {len(scenario["round_leaders"])} rounds.']
        data += ['\n\nScenario:\n']
        data += [dumps(scenario)]

        data += ['\n\nNetwork logs:\n']
        data += [f'{t}\n' for t in network.trace] + ['\n']

        for n in network.nodes.values():
            data += [f'\n\n{n.name} logs:\n']
            data += [f'{t}\n' for t in n.log.log]
            data += [f'\n{n.storage.__repr__()}']

        with open(file_path, 'w') as f:
            f.write(''.join(data))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Twins Executor.')
    parser.add_argument('path', help='path to the scenario file')
    parser.add_argument('--log', help='output log directoru')
    parser.add_argument('-v', action='store_true', help='verbose logging')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.v else logging.INFO,
        format='[%(levelname)s] %(message)s'
    )

    runner = TwinsRunner(args.path, log_path=args.log)
    runner.run()
