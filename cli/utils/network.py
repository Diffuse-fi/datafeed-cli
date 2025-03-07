import os
import subprocess
import enum
import argparse
import sys
from lib.sgx_verifier_deployer.script.utils.network import *

all_pairs = []
with open('pairs/list.txt', 'r') as file:
    pair_names_list = file.read()
    pair_names_list = pair_names_list.split('\n')
    for p in pair_names_list:
        if p.strip() != '':
            all_pairs.append(p.strip())


def parse_pairname(pair_name):
    if pair_name in all_pairs:
        return pair_name
    else:
        raise argparse.ArgumentTypeError(f"Invalid pair: {pair_name}. Possible valies: {all_pairs}")


def address_path(net, contract):
    return 'addresses/' + net.dirname + contract

def run_subprocess(_command, what):
    print(what + "...", end=" ")

    result = subprocess.run(_command, capture_output=True, text=True)

    exit_code = result.returncode

    if (exit_code == 0):
        print("SUCCEEDED")
        return(result.stdout)
    else:
        print("FAILED!")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        sys.exit(1)

def get_proxy_address(net):
    file = open(address_path(net, "proxy"), 'r')
    proxy_address = file.readline().strip()
    file.close()

    return proxy_address


def get_feeder_address(net):
    file = open(address_path(net, "feeder"), 'r')
    data_feeder_address = file.readline().strip()
    file.close()

    return data_feeder_address

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


def call_contract(net, address, signature, params, is_address=False):
    command = [ "cast", "call", "--rpc-url=" + net.rpc_url, address]
    command.append(signature)
    arguments = ""
    for p in params:
        command.append(p)
        arguments += p
    # Neon request works successfully only with --trace and returns error without it
    command.append('--trace')

    result = run_subprocess(command, "call " + signature + " with arguments " + arguments)
    result = result.split("[Return] ")[1].split("\n")[0]
    if is_address==True:
        result = strip_address(result)
    result = result.strip()

    return result

