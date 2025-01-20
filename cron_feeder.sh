#!/bin/bash

# add this script to crontab -e:
# * * * * * /path_to_rep/cron_feededr.sh >> /path_to_rep/cron_log.txt 2>&1

export PATH="$HOME/.cargo/bin:$PATH"
export PATH="/$HOME/.foundry/bin:$PATH"
export PYTHONPATH="$(pwd):$PYTHONPATH"

cd our_org/cron/diffuse-datafeed/ # ~/path/to/repo

source .env

echo "start feeding: $(date)" >> feeding_log.txt
python3 cli/parse_prove_feed.py -n eth_sepolia --binance-zk-local >> feeding_log.txt 2>&1
echo "binance data request and proving finished: $(date)" >> feeding_log.txt

echo "==========================================" >> feeding_log.txt
