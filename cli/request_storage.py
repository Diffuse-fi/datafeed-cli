import subprocess
import sys
from datetime import datetime
from utils.network import *
from lib.sgx_verifier_deployer.script.utils.network import *

class method_enum(enum.Enum):
    DECIMALS = "decimals"
    DESCRIPTION = "description"
    LATEST_ANSWER = "latestAnswer"
    LATEST_ROUND = "latestRound"
    GET_ROUND_DATA = "getRoundData"
    LATEST_ROUND_DATA = "latestRoundData"

def parse_request(value):
    try:
        return method_enum(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid network: {value}. Possible valies: {[n.value for n in method_enum]}")

def get_request_signature(req):
    match req:
        case method_enum.DECIMALS:
            return "decimals()(uint8)"
        case method_enum.DESCRIPTION:
            return "description()(string)"
        case method_enum.LATEST_ANSWER:
            return "latestAnswer()(uint256)"
        case method_enum.LATEST_ROUND:
            return "latestRound()(uint256)"
        case method_enum.GET_ROUND_DATA:
            return "getRoundData(uint80 _roundId) returns (uint80 roundId, uint256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)"
        case method_enum.LATEST_ROUND_DATA:
            return "latestRoundData()(uint80, uint256, uint256, uint256, uint80)"

def do_request(pair, net, req, round=None):
    file = open(address_path(net, pair.value), 'r')
    storage_address = file.readline().strip()
    file.close()

    print("requesting method", req.value)

    command = [
        "cast",
        "call",
        "--rpc-url=" + net.rpc_url,
        storage_address,
        get_request_signature(req)
    ]
    if req == method_enum.GET_ROUND_DATA:
        command.append(str(round))

    result = run_subprocess(command, "request method '" + req.value + "' for " + pair.value)

    if req == method_enum.LATEST_ROUND_DATA or req == method_enum.GET_ROUND_DATA:
        result = result.split("\n")
        print("round number:", result[0])
        print("answer:", result[1], "(price:", int(result[1].split(" [")[0]) / (10**8), ")")

        timestamp = int(int(result[2].split(" [")[0]) / 1000)
        readable_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print("timestamp:", timestamp, "(human readable:)", readable_date)
    else:
        print("result:", result)
    print("===================================")
    return result


def main():
    parser = argparse.ArgumentParser(description="Storage request parameters")
    parser.add_argument('-n', '--network', type=network_class, required=True, help="Choose network (local, sepolia, eth_mainnet)")
    parser.add_argument('-p', '--pair', type=parse_pairname, required=True, help="Choose pair (ETHBTC, BTCUSDT, ETHUSDT, ETHUSDC)")
    parser.add_argument('-m', '--method', type=parse_request, required=True,
        help="Choose request (decimals, description, latestAnswer, latestRound, latestRoundData)")

    parser.add_argument('-r', '--round', type=int, required=False, help="roundID for getRoundData request")

    args = parser.parse_args()

    if args.method == method_enum.GET_ROUND_DATA:
        assert args.round != None, "cmd line argument --round is required for getRoundData!"
        do_request(args.pair, args.network, args.method, args.round)
    else:
        do_request(args.pair, args.network, args.method)

if __name__ == "__main__":
    main()