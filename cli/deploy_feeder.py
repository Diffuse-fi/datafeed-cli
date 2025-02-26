import subprocess
import sys
import os
from utils.network import *
from lib.sgx_verifier_deployer.script.utils.network import *
from lib.sgx_verifier_deployer.script.utils.functions import parse_env_var
from lib.sgx_verifier_deployer.script.utils.wrapper import DCAP_ATTESTATION

def strip_address(addr):
    if addr[:2] != '0x':
        print("expected address starting from '0x', got", addr)

    if len(addr) == 42:
        return addr
    elif len(addr) == 66:
        return '0x' + addr[66 - 42 + 2: ]
    else:
        print("expected ethereum address, got", addr)
        sys.exit(1)


def are_you_sure_not_local(net):
    if net == LOCAL_NETWORK:
        print("deploying DataFeedFeeder to", net.name)
    else:
        while(True):
            user_input = input("You are deploying DataFeeder to " + net.name + " network. Are you sure? [y/n]: ").lower()
            if user_input == 'y':
                break
            elif user_input == 'n':
                print("cancelled execution", file=sys.stderr)
                sys.exit(1)
            else:
                print("Please enter 'y' or 'n'.")
                continue


def set_deployment_command(net):
    deployment_command = ["forge", "script", '--rpc-url=' + net.rpc_url, '--chain-id=' + net.chain_id, "--broadcast", "script/Deploy.s.sol"]
    if net == NEON_DEVNET:
        deployment_command.append("--legacy") # disables some new unsupported in NeonEVM features, must use in Neon
        deployment_command.append("--skip-simulation") # parameter skips the on-chain simulation which doesn't work on Neon EVM , must use in Neon
    return deployment_command


def deploy_data_feeder(net):

    are_you_sure_not_local(net)

    parse_env_var(net, DCAP_ATTESTATION, root="lib/sgx_verifier_deployer/")

    deployment_command = set_deployment_command(net)
    result = run_subprocess(deployment_command, "DataFeedFeeder deployment")

    data_feeder_address = result.split("Deployed DataFeedFeeder to ")[1].split("\n")[0].strip()
    data_feeder_address = strip_address(data_feeder_address)

    if not os.path.exists(os.path.dirname(address_path(net, "feeder"))):
        os.makedirs(os.path.dirname(address_path(net, "feeder")))

    file = open(address_path(net, "feeder"), 'w')
    file.write(data_feeder_address)
    print("wrote feeder address to", address_path(net, "feeder"), "\n======================================")
    file.close()


def request_storage_address(net, pair_name):
    # Neon request works successfully only with --trace and returns error without it
    command = [ "cast", "call", "--rpc-url=" + net.rpc_url, get_feeder_address(net), "getPairStorageAddress(string)(address)", pair_name, "--trace"]

    result = run_subprocess(command, "request DataFeedStorage address for " + pair_name + " ")
    result = result.split("[Return] ")[1].split("\n")[0]
    result = strip_address(result)

    file = open(address_path(net, pair_name), 'w')
    file.write(result.strip())
    file.close()

    print("wrote address to", address_path(net, pair_name), "\n======================================")


def manage_storage_contract(net, prev_feeder, new_feeder, pair_name):
    ownership_transfer_command = [ "cast", "send", prev_feeder, 'transferStorage(string calldata pair_name, address newFeederAddress)', pair_name, new_feeder, "--rpc-url=" + net.rpc_url, "--private-key=" + os.getenv('PRIVATE_KEY')]
    new_deployment_command = [ "cast", "send", new_feeder, 'setNewPair(string)(address)', pair_name, "--rpc-url=" + net.rpc_url, "--private-key=" + os.getenv('PRIVATE_KEY')]

    if prev_feeder is not None:
        storage_address = call_contract(net, prev_feeder, 'dataFeedStorages(string)(address)', [pair_name], is_address=True)
        if int(storage_address, 16) == 0:
            run_subprocess(new_deployment_command, "Deploy storage contract for " + pair_name + " pair")
        else:
            storage_owner = call_contract(net, prev_feeder, 'owner()(address)', [], is_address=True)
            if storage_owner != new_feeder:
                run_subprocess(ownership_transfer_command, "Transfer ownership to new feeder for " + pair_name + " pair")
            else:
                print("new_feeder already owns storage of", pair_name)
    else:
        run_subprocess(new_deployment_command, "Deploy storage contract for " + pair_name + " pair")


def main():
    parser = argparse.ArgumentParser(description="Data feeder parameters")
    parser.add_argument('-n', '--network', type=network_class, required=True, help="Choose network (local, sepolia, eth_mainnet, neon_devnet)")

    args = parser.parse_args()

    previous_feeder = None
    if os.path.isfile(address_path(args.network, "feeder")) == True:
        previous_feeder = get_feeder_address(args.network)
    deploy_data_feeder(args.network)
    new_feeder = get_feeder_address(args.network)
    print("previous_feeder:", previous_feeder)
    print("new_feeder:", new_feeder)

    for p in pair_name_enum:
        manage_storage_contract(args.network, previous_feeder, new_feeder, p.value)


if __name__ == "__main__":
    main()