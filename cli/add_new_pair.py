import subprocess
import sys
import os
from utils.network import *
from lib.sgx_verifier_deployer.script.utils.network import *
from lib.sgx_verifier_deployer.script.utils.functions import parse_env_var
from lib.sgx_verifier_deployer.script.utils.wrapper import DCAP_ATTESTATION



import requests
import json

def check_if_binance_has_this_pair(pair_name):
    BASE_URL = "https://data-api.binance.vision/"

    endpoint = f"{BASE_URL}/api/v3/ticker/price?symbol=" + pair_name
    response = requests.get(endpoint)

    data = response.json()

    if response.status_code == 400 and (data['code'] == -1100 or data['code'] == -1121):
        raise argparse.ArgumentTypeError(f"Pair {pair_name} is not listed on binance")
    elif response.status_code != 200:
        raise Exception(f"Error {response.status_code} - {response.text}")
    print(data)


def add_pair(pair_name):
    check_if_binance_has_this_pair(pair_name)

    with open('pairs/list.txt', 'r') as file:
        pairs_list = file.read()
        last_symbol = pairs_list[-1]
        if pair_name in pairs_list.split('\n'):
            print("pair", pair_name, "is already added")
            return
    with open('pairs/list.txt', 'a') as file:
        if last_symbol != '\n':
            file.write("\n")
        file.write(pair_name + "\n")


def main():
    parser = argparse.ArgumentParser(description="New pair addition parameters")
    parser.add_argument('-p', '--pair-name', type=str, required=True, help="Pair you want to add")

    args = parser.parse_args()
    add_pair(args.pair_name)


if __name__ == "__main__":
    main()

