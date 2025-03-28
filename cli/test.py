import subprocess
import time
import sys

from utils.network import *
from deploy_feeder import deploy_data_feeder, manage_storage_contract
from deploy_proxy import deploy_proxy
from add_new_pair import add_pair
from feed_feeder import feed_data
from request_storage import do_request
from request_storage import method_enum
from parse_and_prove import prepare_json

from lib.sgx_verifier_deployer.script.utils.network import *

def test(test_data, binance_zk_bonsai, binance_zk_local):

    assert test_data + binance_zk_bonsai + binance_zk_local == 1, "test requires exactly one flag"

    pair_1 = "BTCUSDT"
    pair_2 = "USDCUSDT"

    step = 0
    print(f"step {step}: set env variables...")
    anvil_testnet_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    os.environ["ETH_WALLET_PRIVATE_KEY"] = anvil_testnet_private_key
    os.environ["PRIVATE_KEY"] = anvil_testnet_private_key
    os.environ["ALCHEMY_API_KEY"] = "placeholder"

    step+=1
    print(f"step {step}: clean addresses/local/...")
    feeder_addr = 'addresses/local/feeder'
    if os.path.exists(feeder_addr) == True:
        os.remove(feeder_addr)

    step+=1
    print(f"step {step}: deploying datafeed proxy...")
    deploy_proxy(LOCAL_NETWORK)

    step+=1
    print(f"step {step}: deploying datafeed feeder...")
    deploy_data_feeder(LOCAL_NETWORK)
    old_feeder = get_feeder_address(LOCAL_NETWORK)

    step+=1
    print(f"step {step}: requesting storage addresses...")
    for pair_name in all_pairs:
        manage_storage_contract(LOCAL_NETWORK, None, old_feeder, pair_name)

    step+=1
    print(f"step {step}: request data from binance...")
    prepare_json(LOCAL_NETWORK, False, True, False, False, "pairs/test.txt")

    step+=1
    print(f"step {step}: Print traces of feeding execution...")
    feed_data(LOCAL_NETWORK, is_zk=False, trace=True)

    step+=1
    print(f"step {step}: Feed feeder (onchain) and check rounds amount in storage contract...")
    feed_data(LOCAL_NETWORK, is_zk=False, trace=False)
    rounds_amount = do_request(pair_1, LOCAL_NETWORK, method_enum.LATEST_ROUND).strip()
    assert rounds_amount == "0", "rounds amount must be 0 after upload, but it is " + rounds_amount + " something is wrong"


    step+=1
    print(f"step {step}: request and prove data from binance...")
    prepare_json(LOCAL_NETWORK, False, False, binance_zk_bonsai, binance_zk_local, "pairs/test.txt")

    step+=1
    print(f"step {step}: Print traces of feeding execution(zk)...")
    feed_data(LOCAL_NETWORK, is_zk=True, trace=True)

    step+=1
    print(f"step {step}: Feed feeder (onchain) and check rounds amount in storage contract...")
    feed_data(LOCAL_NETWORK, is_zk=True, trace=False)
    rounds_amount = do_request(pair_1, LOCAL_NETWORK, method_enum.LATEST_ROUND).strip()
    assert rounds_amount == "1", "rounds amount must be 1 after upload, but it is " + rounds_amount + " something is wrong"


    step+=1
    print(f"step {step}: request storages...")
    for p in all_pairs:
        for m in method_enum:
            if m == method_enum.GET_ROUND_DATA:
                do_request(p, LOCAL_NETWORK, m, 0)
            else:
                do_request(p, LOCAL_NETWORK, m)

    step+=1
    print(f"step {step}: adding new pair...")
    add_pair(pair_2)
    all_pairs.append(pair_2)

    step+=1
    print(f"step {step}: redeploying datafeed feeder...")
    deploy_data_feeder(LOCAL_NETWORK)
    new_feeder = get_feeder_address(LOCAL_NETWORK)

    step+=1
    print(f"step {step}: requesting storage addresses...")
    for pair_name in all_pairs:
        manage_storage_contract(LOCAL_NETWORK, old_feeder, new_feeder, pair_name)

    step+=1
    print(f"step {step}: request data from binance...")
    prepare_json(LOCAL_NETWORK, False, True, False, False, None)

    step+=1
    print(f"step {step}: Print traces of feeding execution...")
    feed_data(LOCAL_NETWORK, is_zk=False, trace=True)

    step+=1
    print(f"step {step}: Feed feeder (onchain) and check rounds amount in storage contract...")
    feed_data(LOCAL_NETWORK, is_zk=False, trace=False)
    rounds_amount = do_request(pair_1, LOCAL_NETWORK, method_enum.LATEST_ROUND).strip()
    assert rounds_amount == "2", "rounds amount must be 2 after upload, but it is " + rounds_amount + " something is wrong"
    rounds_amount = do_request(pair_2, LOCAL_NETWORK, method_enum.LATEST_ROUND).strip()
    assert rounds_amount == "0", "rounds amount must be 0 for " + pair_2 + " after upload, but it is " + rounds_amount + " something is wrong"

    step+=1
    print(f"step {step}: request and prove data from binance...")
    prepare_json(LOCAL_NETWORK, False, False, binance_zk_bonsai, binance_zk_local, None)

    step+=1
    print(f"step {step}: Print traces of feeding execution(zk)...")
    feed_data(LOCAL_NETWORK, is_zk=True, trace=True)

    step+=1
    print(f"step {step}: Feed feeder (onchain) and check rounds amount in storage contract...")
    feed_data(LOCAL_NETWORK, is_zk=True, trace=False)
    rounds_amount = do_request(pair_1, LOCAL_NETWORK, method_enum.LATEST_ROUND).strip()
    assert rounds_amount == "3", "rounds amount must be 3 for " + pair_1 + " after upload, but it is " + rounds_amount + " something is wrong"
    rounds_amount = do_request(pair_2, LOCAL_NETWORK, method_enum.LATEST_ROUND).strip()
    assert rounds_amount == "1", "rounds amount must be 1 for " + pair_2 + " after upload, but it is " + rounds_amount + " something is wrong"


    step+=1
    print(f"step {step}: clean addresses/local/...")
    feeder_addr = 'addresses/local/feeder'
    if os.path.exists(feeder_addr) == True:
        os.remove(feeder_addr)

parser = argparse.ArgumentParser(description="test parameters")

test_config = parser.add_mutually_exclusive_group()
test_config.add_argument('--test-data', action='store_true', help='Use already proven test set (blazingly fast)')
test_config.add_argument('--binance-zk-bonsai', action='store_true', help='Request data from binance and prove using bonsai (quite fast and checks proving process)')
test_config.add_argument('--binance-zk-local', action='store_true', help='Request data from binance and prove locally (15 minutes but checks that local proving works)')

args = parser.parse_args()

test(args.test_data, args.binance_zk_bonsai, args.binance_zk_local)
