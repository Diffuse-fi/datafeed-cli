import subprocess
import sys
from utils.network import *
from lib.sgx_verifier_deployer.script.utils.network import *
from lib.sgx_verifier_deployer.script.utils.functions import parse_env_var
from lib.sgx_verifier_deployer.script.utils.wrapper import DCAP_ATTESTATION


def fun(net):

    parse_env_var(net, DCAP_ATTESTATION, root="lib/sgx_verifier_deployer/")

    cmd = [
        "cast",
        "abi-encode",
        "f(address)",
        os.getenv('DCAP_ATTESTATION')
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        print("res.stdout:", res.stdout)
        print("res.stderr:", res.stderr)
        sys.exit(1)
    abi_encoded_dcap_address = res.stdout.strip()
    print("abi_encoded_dcap_address:", abi_encoded_dcap_address)


    cmd = [
        'forge',
        'verify-contract',
        '--chain-id=' + str(net.chain_id),
        get_feeder_address(net),
        'contracts/DataFeedFeeder.sol:DataFeedFeeder',
        '--etherscan-api-key=' + os.getenv('ETHERSCAN_API_KEY'),
        '--watch',
        '--constructor-args=' + abi_encoded_dcap_address
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    print("res.stdout:", res.stdout)
    print("res.stderr:", res.stderr)

    if res.returncode != 0:
        print("res.returncode:", res.returncode)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Data feeder parameters")
    parser.add_argument('-n', '--network', type=network_class, required=True, help="Choose network (local, sepolia, eth_mainnet, neon_devnet)")
    args = parser.parse_args()
    fun(args.network)


if __name__ == "__main__":
    main()