import subprocess
import sys
from utils.network import *
from lib.sgx_verifier_deployer.script.utils.network import *

def verify_storage(net, pair_name):

    pair_address =  call_contract(net, get_feeder_address(net), "getPairStorageAddress(string)(address)", [pair_name], is_address=True)

    cmd = [
        "cast",
        "abi-encode",
        "f(string memory _description_string, uint8 _decimals_amount)",
        pair_name,
        "8"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        print("res.stdout:", res.stdout)
        print("res.stderr:", res.stderr)
        sys.exit(1)
    abi_encoded_constructor_args = res.stdout.strip()
    print("abi_encoded_constructor_args:", abi_encoded_constructor_args)
    cmd = [
        'forge',
        'verify-contract',
        '--rpc-url',
        'https://testnet-rpc.monad.xyz',
        '--verifier',
        'sourcify',
        '--verifier-url',
        'https://sourcify-api-monad.blockvision.org',
        pair_address,
        'contracts/DataFeedStorage.sol:DataFeedStorage',

        # '--etherscan-api-key=' + os.getenv('ETHERSCAN_API_KEY'),
        # '--watch',
        # '--constructor-args=' + abi_encoded_constructor_args
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
        'https://testnet-rpc.monad.xyz',
        '--verifier',
        'sourcify',
        '--verifier-url',
        'https://sourcify-api-monad.blockvision.org',
        get_feeder_address(net),
        'contracts/DataFeedFeeder.sol:DataFeedFeeder',
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
    # verify_feeder(args.network)
    for pair_name in pair_names_list:
        verify_storage(args.network, pair_name)



if __name__ == "__main__":
    main()


#     forge verify-contract \
#   --rpc-url https://testnet-rpc.monad.xyz \
#   --verifier sourcify \
#   --verifier-url 'https://sourcify-api-monad.blockvision.org' \
#   0xF27E6e2Ad3e3c24c44adC271fC8576357474BAE0 \
#   contracts/DataFeedProxy.sol:DataFeedProxy
