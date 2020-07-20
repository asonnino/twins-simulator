<a href="https://novi.com/">
	<img width="100" src=".assets/novi.png" alt="Novi Logo" />
</a>

<hr/>


# Twins Simulator
[![License](https://img.shields.io/badge/license-Apache-green.svg)](LICENSE.md)

This repository is dedicated to sharing material related to the Twins Simulator, developed at Novi Financial (formerly Calibra). Software is provided for research-purpose only and is not meant to be used in production.

## Summary
Twins is a new approach for testing BFT systems. The main idea of Twins is that we can emulate Byzantine behavior by running two (or generally up to k) instances of a node with the same identity. Each of the two instances (or Twins) runs unmodified, correct code. The Twins approach requires only a thin network wrapper that delivers messages to/from both Twins.

This repo provides software to execute Twins scenarios on a simulation of the [Streamlet consensus protocol](https://eprint.iacr.org/2020/088.pdf).

## Install
It is advised to first create a virtual environment:
```
$ virtualenv venv
$ source venv/bin/activate
```
Then run:
```
$ pip install -e .
```

## Tests
Tests and simulations are run with `pytest`:
```
$ pip install pytest
$ pytest
```
To run a specific simulation, you can also run:
```
$ pytest -s -k TEST_NAME # Where TEST_NAME is the name of the test function
$ pytest -s -k test_happy # Example
```

If you have `tox` installed, simply run:
```
$ tox
```

## Run
The script `twins_executor` allows to run Twins scenarios from json files:
```
$ python scripts/twins_executor.py scripts/test_scenarios.json
```
See [Twins Generator](https://github.com/novifinancial/twins-generator) for instruction on how to generate scenario files.

## References
* [Twins: White-Glove Approach for BFT Testing](https://arxiv.org/abs/2004.10617)
* [Twins Generator](https://github.com/novifinancial/twins-generator)

## License
The content of this repository is licensed as [Apache 2.0](https://github.com/novifinancial/twins-simulator/blob/master/LICENSE)
