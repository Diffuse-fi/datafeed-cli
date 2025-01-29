# Repo for requesting data from wesites using intel SGX and publishing it on-chain.

## Overwiev
Price data for pairs listed in pairs/list.txt is requested from binance.com inside the trusted execution environment. sgx_quote vaildity guarantees that data is correst. Sgx quote is verified either on chain (more expensive but does not require timely zk proving off chain) or insize the zkVM, it reduces on-chain verification pruce, but requires some time to create zk proof.

## Instruction
1. Clone repo:
```
git clone https://github.com/Diffuse-fi/diffuse-datafeed
cd diffuse-datafeed
git submodule update --init --recursive
```

2. Go to sgx-scaffold and build it according to its readme file. If all prerequisites are installed then it will look like this:
```
cd lib/sgx-scaffold
cargo sgx build
cd -
```

3. Go to sgx-scaffold and build it according to its readme file. If all prerequisites are installed then it will look like this:
```
cd lib/automata-dcap-zkvm-cli/dcap-bonsai-cli/
cargo build --release
cd -
```

4. (optional) If you want to work on the local node, launch anvil:
```
anvil
```
and switch to another tab

5. (optional) Go to cd lib/sgx_verifier_deployer/ and deploy infrastructure/update collaterals on chain. Needed if you are working on fresh local node.

6. export current location to PYTONPATH:
```
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

7. Create .env file and write all needed env variables listed in .env.example. Source the env variables:
```
source .env
```

8. There is cli for interactions with chain.

Deploy (expample for local network):
```
python3 cli/delpoy_feeder.py -n local
```

Parse price data (example for local network, on-chain zk verification and proving with bonsai):
```
python3 cli/parse_and_prove.py -n local --binance-zk-bonsai
```

Publish data on chain (example for local network using zk proof from zkVM):
```
python3 cli/feed_feeder.py -n local --zk
```

Request data from chain (example for requesting latest round data for BTCUSDT from local network):
```
python3 cli/request_storage.py -n local -p BTCUSDT -m latestRoundData
```
