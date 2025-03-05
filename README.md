# Data Feed CLI

## Overview
This repository provides a CLI for Diffuse Data Feeds powered by zk Serverless. In its current state, the on-chain endpoints provide the latest information about the Price Pairs from CEXs and DEXs. The product is currently in the testnet phase, and Binance is used as a data provider.

---
Reach out for any collaboration. We are constantly growing the number of chains and the list of supported data. If you need fast and trustless Data Feeds of your favourite token on your favourite chain - you know what to do:

[![X (formerly Twitter) URL](https://img.shields.io/twitter/follow/diffusefi)](https://x.com/diffusefi)

---

## Instruction
1. Clone repo:
```
git clone https://github.com/Diffuse-fi/datafeed-cli
cd ´datafeed-cli´
git submodule update --init --recursive
```

2. Go to `zktls-enclave` and build the enclave according to the readme file. If all prerequisites are installed then it will look like this:
```
cd lib/zktls-enclave
cargo sgx build
cd -
```

3. Go to the CLI directory for Bonsai and build it. If all prerequisites are installed then it will look like this:
```
cd lib/automata-dcap-zkvm-cli/dcap-bonsai-cli/
cargo build --release
cd -
```

4. (optional) If you want to work on the local node, launch `anvil`:
```
anvil
```
and switch to another tab

5. (optional) Go to cd `lib/sgx_verifier_deployer/` and deploy on-chain infrastructure or update collaterals. This is also needed if you are working on a fresh local node.

6. export current location to `PYTHONPATH`:
```
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

7. Create an `.env` file and write all needed env variables listed in `.env.example`. Then source the env variables:
```
source .env
```

8. There is a CLI for interactions with the deployed endpoint.

There are three contracts: proxy, feeder and storage.
Storage contract stores price data, every pair has its own storage. Only owner can upload data to storages.
Feeder contract owns all storage contracts. It receives proofs, verifies them and uploads data to storages after verification. It guarantees that only proven data is stored in storage contracts.
Proxy contract contains list of all pairs and storage addresses. It has predetermined address on all chains because CREATE2 insrtuction is used for deployment. Deployed only once.


Deploy (example for the local network):
For the first time you will need to deploy proxy, skip this step if you are redeploying feeder:
```
python3 cli/delpoy_proxy.py -n local
```
then deploy feeder:
```
python3 cli/delpoy_feeder.py -n local
```

Parse price data (example for the local network, off-chain verification and proving with bonsai):
```
python3 cli/parse_and_prove.py -n local --binance-zk-bonsai
```

Publish data on chain (example for the local network using zk proof from zkVM):
```
python3 cli/feed_feeder.py -n local --zk
```

Request data from chain (example for requesting latest round data for BTCUSDT from local network):
```
python3 cli/request_storage.py -n local -p BTCUSDT -m latestRoundData
```

## How to add new pairs
Pairs are listed in `pairs/list.txt`, please use `cli/add_new_pair.py` to add new pairs, it checks if pair was already added and is listed on binance.
