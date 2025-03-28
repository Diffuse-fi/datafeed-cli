import subprocess
import sys
from utils.network import *
from lib.sgx_verifier_deployer.script.utils.network import *

def verify_storage(net, pair_name):

    pair_address =  call_contract(net, get_feeder_address(net), "getPairStorageAddress(string)(address)", [pair_name], is_address=True)

    cmd = [
        'forge',
        'verify-contract',
        '--rpc-url',
        'https://automata-mainnet.alt.technology',
        '--verifier',
        'blockscout',
        '--verifier-url',
        'https://automata-mainnet-explorer.alt.technology:443/api/',
        pair_address,
        'contracts/DataFeedStorage.sol:DataFeedStorage',
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    print("res.stdout:", res.stdout)
    print("res.stderr:", res.stderr)

    if res.returncode != 0:
        print("res.returncode:", res.returncode)
        sys.exit(1)


def verify_feeder(net):
    cmd = [
        'forge',
        'verify-contract',
        '--rpc-url',
        'https://automata-mainnet.alt.technology',
        '--verifier',
        'blockscout',
        '--verifier-url',
        'https://automata-mainnet-explorer.alt.technology:443/api/',
        get_feeder_address(net),
        'contracts/DataFeedFeeder.sol:DataFeedFeeder',
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    print("res.stdout:", res.stdout)
    print("res.stderr:", res.stderr)

    if res.returncode != 0:
        print("res.returncode:", res.returncode)
        sys.exit(1)

def verify_proxy(net):
    cmd = [
        'forge',
        'verify-contract',
        '--rpc-url',
        'https://automata-mainnet.alt.technology',
        '--verifier',
        'blockscout',
        '--verifier-url',
        'https://automata-mainnet-explorer.alt.technology:443/api/',
        get_proxy_address(net),
        'contracts/DataFeedProxy.sol:DataFeedProxy',
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    print("res.stdout:", res.stdout)
    print("res.stderr:", res.stderr)

    if res.returncode != 0:
        print("res.returncode:", res.returncode)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Data feeder parameters")
    parser.add_argument('-n', '--network', type=network_class, required=True, help="Choose network (" + networks_str + ")")
    args = parser.parse_args()
    verify_proxy(args.network)
    verify_feeder(args.network)
    for pair_name in pair_names_list:
        verify_storage(args.network, pair_name)



if __name__ == "__main__":
    main()

