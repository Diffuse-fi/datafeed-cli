import os
import subprocess
import enum
import argparse
import sys
from lib.sgx_verifier_deployer.script.utils.network import *

# hardcoded pairs
class pair_name_enum(enum.Enum):
    ETHBTC = "ETHBTC"
    BTCUSDT = "BTCUSDT"
    ETHUSDT = "ETHUSDT"
    ETHUSDC = "ETHUSDC"
    SOLUSDT = "SOLUSDT"
    TRUMPUSDT = "TRUMPUSDT"
    TRUMPUSDC = "TRUMPUSDC"

def parse_pairname(value):
    try:
        return pair_name_enum(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid network: {value}. Possible valies: {[n.value for n in pair_name_enum]}")


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



def get_feeder_address(net):
    file = open(address_path(net, "feeder"), 'r')
    data_feeder_address = file.readline().strip()
    file.close()

    return data_feeder_address
