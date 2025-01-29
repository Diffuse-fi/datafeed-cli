import sys
import argparse
from utils.network import *
from lib.sgx_verifier_deployer.script.utils.functions import parse_env_var
from lib.sgx_verifier_deployer.script.utils.wrapper import PCS_DAO, FMSPC_TCB_DAO, ENCLAVE_ID_DAO, DCAP_ATTESTATION

def find_latest_data():
    latest_data = -1

    os.makedirs("data/", exist_ok=True)

    existing_data = os.listdir("data/")
    for d in existing_data:
        if (d.isdigit() == True):
            latest_data = max(latest_data, int(d))
    return latest_data

def prepare_json (net, _test_data, _binance_onchain, _binance_zk_bonsai, _binance_zk_local):

    assert _test_data + _binance_onchain + _binance_zk_bonsai + _binance_zk_local == 1, "exactly one of flags is required"

    new_data_dir = "data/" + str(find_latest_data() + 1) + "/"
    os.makedirs(new_data_dir)

    files_1 = ["pairs.bin", "prices.bin", "timestamps.bin", "sgx_quote.bin"]
    files_2 = ["sgx_verification_journal.bin", "sgx_verification_seal.bin"]

    if _test_data == True:
        for f in files_1:
            run_subprocess(["cp", "cli/test_data/0/" + f, new_data_dir + f], "copy" + " cli/test_data/0/" + f + " to" + new_data_dir + f)
        for f in files_2:
            run_subprocess(["cp", "cli/test_data/0/" + f, new_data_dir + f], "copy" + " cli/test_data/0/" + f + " to" + new_data_dir + f)
        return
    else:
        parse_env_var(net, PCS_DAO, root="lib/sgx_verifier_deployer/")
        parse_env_var(net, FMSPC_TCB_DAO, root="lib/sgx_verifier_deployer/")
        parse_env_var(net, ENCLAVE_ID_DAO, root="lib/sgx_verifier_deployer/")
        parse_env_var(net, DCAP_ATTESTATION, root="lib/sgx_verifier_deployer/")
        os.environ["RPC_URL"] = net.rpc_url

        run_subprocess(["./lib/sgx-scaffold/target/debug/app-template"], "request from binance using sgx")
        for f in files_1:
            run_subprocess(["mv", f, new_data_dir + f], "move requested " + f + " to " + new_data_dir)
        if _binance_onchain == True:
            return

        zkvm_cli_cmd = ["./lib/automata-dcap-zkvm-cli/target/release/dcap-bonsai-cli", "prove", "-p", new_data_dir + "sgx_quote.bin"]
        if _binance_zk_local == True:
            zkvm_cli_cmd.append("--local-proving")

        run_subprocess(zkvm_cli_cmd, "prove sgx_quote verification")

        for f in files_2:
            run_subprocess(["mv", f, new_data_dir + f], "move requested " + f + " to " + new_data_dir)



def main():
    parser = argparse.ArgumentParser(description="Data feeder parameters")

    parser.add_argument('-n', '--network', type=network_class, required=True, help="Choose network (local, sepolia, eth_mainnet, neon_devnet)")

    data_source_group = parser.add_mutually_exclusive_group()
    data_source_group.add_argument('--test-data', action='store_true', help='Use already proven test set')
    data_source_group.add_argument('--binance-onchain', action='store_true', help='Request data from binance, no proving (no time spent on proving but more expensive on-chain verification)')
    data_source_group.add_argument('--binance-zk-bonsai', action='store_true', help='Request data from binance and prove using bonsai (quite fast and checks proving process)')
    data_source_group.add_argument('--binance-zk-local', action='store_true', help='Request data from binance and prove locally (15 minutes but checks that local proving works)')

    args = parser.parse_args()

    prepare_json(args.network, args.test_data, args.binance_onchain, args.binance_zk_bonsai, args.binance_zk_local)

if __name__ == "__main__":
    main()
