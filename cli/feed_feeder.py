import sys
import argparse
from utils.network import *
from lib.sgx_verifier_deployer.script.utils.network import *

def find_latest_data():
    latest_data = -1

    os.makedirs("data/", exist_ok=True)

    existing_data = os.listdir("data/")
    for d in existing_data:
        if (d.isdigit() == True):
            latest_data = max(latest_data, int(d))
    return latest_data


def text_array_from_binary_file(filename, isdigit):
    with open(filename, "rb") as f:
        data = f.read()
    text = data.decode("utf-8")
    text = text.rstrip('\x00')
    text = text.split('\n')

    if isdigit == True:
        quotation = ''
    else:
        quotation = '"'

    array = "["
    for line in text:
        if line != '\n':
            line = line.strip()
            line = quotation + line + quotation + ', '
            array += line
    array = array[:-2]
    array += "]"
    return array


def feed_data(net, is_zk, trace):
    latest_data_dir = "data/" + str(find_latest_data()) + "/"

    pairs = text_array_from_binary_file(latest_data_dir + "pairs.bin", False)
    prices = text_array_from_binary_file(latest_data_dir + "prices.bin", True)
    timestamps = text_array_from_binary_file(latest_data_dir + "timestamps.bin", True)

    if is_zk == True:
        with open(latest_data_dir + "sgx_verification_seal.bin", "rb") as file:
            bin_sgx_verification_seal = file.read()
            hex_sgx_verification_seal = '0x' + bin_sgx_verification_seal.hex()

        with open(latest_data_dir + "sgx_verification_journal.bin", "rb") as file:
            bin_sgx_verification_journal = file.read()
            if bin_sgx_verification_journal:
                hex_sgx_verification_journal = '0x' + bin_sgx_verification_journal.hex()
    else:
        with open(latest_data_dir + "sgx_quote.bin", "rb") as file:
            bin_sgx_quote = file.read()
            hex_sgx_quote = '0x' + bin_sgx_quote.hex()


    with open("pairs/amount.txt", "r") as file:
        pairs_amount = file.read().strip()

    if is_zk == True:
        method_signature = "set_zk(string[" + pairs_amount + "] calldata pair_names,uint256[" + pairs_amount + "] calldata prices,uint256[" + pairs_amount + "] calldata timestamps,bytes calldata sgx_verification_journal,bytes calldata sgx_verification_seal)"
    else:
        method_signature = "set_onchain(string[" + pairs_amount + "] calldata pair_names,uint256[" + pairs_amount + "] calldata prices,uint256[" + pairs_amount + "] calldata timestamps,bytes calldata sgx_quote)"

    command = [
        "cast",
        "send",
        "--private-key=" + os.getenv("ETH_WALLET_PRIVATE_KEY"),
        "--rpc-url=" + net.rpc_url,
        get_feeder_address(net),
        method_signature,
        pairs,
        prices,
        timestamps
    ]
    if is_zk == True:
        command.append(hex_sgx_verification_journal)
        command.append(hex_sgx_verification_seal)
    else:
        command.append(hex_sgx_quote)

    if trace == True:
        command[1] = "call"
        command.append("--trace")
        result = subprocess.run(command)
        print(result.stdout)
    else:
        run_subprocess(command, "DataFeeder feeding")

def main():
    parser = argparse.ArgumentParser(description="Data feeder parameters")
    parser.add_argument('-n', '--network', type=network_class, required=True, help="Choose network (local, sepolia, eth_mainnet, neon_devnet)")
    parser.add_argument('--trace', action='store_true', default=False, help="Print trace level logs using 'cast call --trace'")

    parser.add_argument('--zk', action='store_true', default=False, help="Use risc0 groth16 proof of quote verification")
    parser.add_argument('--onchain', action='store_true', default=False, help="Verify quote onchain")

    args = parser.parse_args()

    assert args.zk + args.onchain == 1, "Chose zk or onchain quote verification method using --zk or --onchain flag"

    feed_data(args.network, args.zk, args.trace)

if __name__ == "__main__":
    main()
