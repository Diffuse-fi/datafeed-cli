
import argparse
from utils.network import *
import fcntl

from parse_and_prove import prepare_json
from feed_feeder import feed_data

def main():
    parser = argparse.ArgumentParser(description="Data feeder parameters")

    parser.add_argument('-n', '--network', type=network_class, required=True, help="Choose network (local, sepolia, eth_mainnet, neon_devnet)")

    data_source_group = parser.add_mutually_exclusive_group()
    data_source_group.add_argument('--test-data', action='store_true', help='Use already proven test set')
    data_source_group.add_argument('--binance-onchain', action='store_true', help='Request data from binance, no proving (no time spent on proving but more expensive on-chain verification)')
    data_source_group.add_argument('--binance-zk-bonsai', action='store_true', help='Request data from binance and prove using bonsai (quite fast and checks proving process)')
    data_source_group.add_argument('--binance-zk-local', action='store_true', help='Request data from binance and prove locally (15 minutes but checks that local proving works)')

    args = parser.parse_args()

    LOCK_FILE = "/tmp/local_proving_in_progress.lock"

    if (args.binance_zk_local == True):
        try:
            with open(LOCK_FILE, 'w') as lock_file:
                fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                print("locking /tmp/local_proving_in_progress.lock to avoid two prover instances in parallel...")
                prepare_json(args.network, args.test_data, False, args.binance_zk_bonsai, args.binance_zk_local)
                feed_data(args.network, is_zk=True, trace=False)
                sys.exit(0)
        except BlockingIOError:
            print("/tmp/local_proving_in_progress.lock is locked, local proving is already in progress. Try later. Exiting.")
            sys.exit(0)


    prepare_json(args.network, args.test_data, args.binance_onchain, args.binance_zk_bonsai, args.binance_zk_local)
    if args.binance_onchain == True:
        is_zk = False
    else:
        is_zk = True
    feed_data(args.network, is_zk, False)

if __name__ == "__main__":
    main()
