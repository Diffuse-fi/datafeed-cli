import subprocess
import sys
import os
from utils.network import *
from lib.sgx_verifier_deployer.script.utils.network import *


def are_you_sure_not_local(net):
    if net == LOCAL_NETWORK:
        print("deploying DataFeedProxy to", net.name)
    else:
        while(True):
            user_input = input("You are deploying DataFeedProxy to " + net.name + " network. Are you sure? [y/n]: ").lower()
            if user_input == 'y':
                break
            elif user_input == 'n':
                print("cancelled execution", file=sys.stderr)
                sys.exit(1)
            else:
                print("Please enter 'y' or 'n'.")
                continue


def set_deployment_command(net):
    deployment_command = ["forge", "script", '--rpc-url=' + net.rpc_url, '--chain-id=' + net.chain_id, "--broadcast", "script/DeployProxy.sol"]
    if net == NEON_DEVNET:
        deployment_command.append("--legacy") # disables some new unsupported in NeonEVM features, must use in Neon
        deployment_command.append("--skip-simulation") # parameter skips the on-chain simulation which doesn't work on Neon EVM , must use in Neon
    return deployment_command


def deploy_proxy(net):

    are_you_sure_not_local(net)


    deployment_command = set_deployment_command(net)
    result = run_subprocess(deployment_command, "DataFeedProxy deployment")

    proxy_address = result.split("Deployed DataFeedProxy to ")[1].split("\n")[0].strip()
    proxy_address = strip_address(proxy_address)

    if not os.path.exists(os.path.dirname(address_path(net, "proxy"))):
        os.makedirs(os.path.dirname(address_path(net, "proxy")))

    file = open(address_path(net, "proxy"), 'w')
    file.write(proxy_address)
    print("wrote proxy address to", address_path(net, "proxy"), "\n======================================")
    file.close()


def main():
    parser = argparse.ArgumentParser(description="datafeed proxy parameters")
    parser.add_argument('-n', '--network', type=network_class, required=True, help="Choose network (local, sepolia, eth_mainnet, neon_devnet)")

    args = parser.parse_args()

    deploy_proxy(args.network)

if __name__ == "__main__":
    main()