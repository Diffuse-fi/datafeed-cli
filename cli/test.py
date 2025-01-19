import subprocess
import time
import sys

from utils.network import *
from deploy_feeder import deploy_data_feeder, request_storage_addresses
from feed_feeder import feed_data
from feed_feeder import feed_data_legacy
from request_storage import do_request
from request_storage import method_enum
from parse_and_prove import prepare_json

from lib.sgx_verification_infrastructure_deployer.script.utils.network import *

def test(test_data, binance_zk_bonsai, binance_zk_local):

    assert test_data + binance_zk_bonsai + binance_zk_local == 1, "test requires exactly one flag"

    step = 0
    step+=1
    print(f"step {step}: set env variables...")
    anvil_testnet_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    os.environ["ETH_WALLET_PRIVATE_KEY"] = anvil_testnet_private_key
    os.environ["ALCHEMY_API_KEY"] = "placeholder"


    step+=1
    print(f"step {step}: deploying datafeed feeder...")
    deploy_data_feeder(LOCAL_NETWORK)

    step+=1
    print(f"step {step}: requesting storage addresses...")
    for p in pair_name_enum:
        request_storage_addresses(LOCAL_NETWORK, p.value)

    step+=1
    print(f"step {step}: copy test data to working directory...")
    prepare_json(LOCAL_NETWORK, test_data, binance_zk_bonsai, binance_zk_local)

    step+=1
    print(f"step {step}: Print traces of feeding execution...")
    feed_data_legacy(LOCAL_NETWORK, True)

    step+=1
    print(f"step {step}: feed feeder and check rounds amount in storage contract...")
    feed_data(LOCAL_NETWORK, False)
    rounds_amount = do_request(pair_name_enum.BTCUSDT, LOCAL_NETWORK, method_enum.LATEST_ROUND).strip()
    assert rounds_amount == "0", "rounds amount must be 0 after upload, but it is " + rounds_amount + " something is wrong"

    step+=1
    print(f"step {step}: feed feeder and check rounds amount in storage contract again...")
    feed_data(LOCAL_NETWORK, False)
    rounds_amount = do_request(pair_name_enum.BTCUSDT, LOCAL_NETWORK, method_enum.LATEST_ROUND).strip()
    assert rounds_amount == "1", "rounds amount must be 1 after upload, but it is " + rounds_amount + " something is wrong"

    step+=1
    print(f"step {step}: feed feeder legacy (neon compatible)...")
    feed_data_legacy(LOCAL_NETWORK, False)

    step+=1
    print(f"step {step}: request storages...")
    for p in pair_name_enum:
        for m in method_enum:
            if m == method_enum.GET_ROUND_DATA:
                do_request(p, LOCAL_NETWORK, m, 0)
            else:
                do_request(p, LOCAL_NETWORK, m)

parser = argparse.ArgumentParser(description="test parameters")

test_config = parser.add_mutually_exclusive_group()
test_config.add_argument('--test-data', action='store_true', help='Use already proven test set (blazingly fast)')
test_config.add_argument('--binance-zk-bonsai', action='store_true', help='Request data from binance and prove using bonsai (quite fast and checks proving process)')
test_config.add_argument('--binance-zk-local', action='store_true', help='Request data from binance and prove locally (15 minutes but checks that local proving works)')

args = parser.parse_args()

test(args.test_data, args.binance_zk_bonsai, args.binance_zk_local)
