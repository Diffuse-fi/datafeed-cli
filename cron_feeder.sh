#!/bin/bash

# add this script to cron:
# */20 * * * * /home/sgx_machine/datafeed_prod/datafeed-cli/feeder.sh > /home/sgx_machine/datafeed_prod/datafeed-cli/cron_log.txt


export PATH="$HOME/.cargo/bin:$PATH"
export PATH="/$HOME/.foundry/bin:$PATH"

cd datafeed_prod/datafeed-cli

source .env
source lib/sgx_verifier_deployer/.env

echo "start parsing: $(date)" >> feeding_log.txt 2>&1
python cli/parse_and_prove.py -n ata_mainnet --binance-zk-local --pairs-file-path=pairs/every_10_minutes.txt  >> feeding_log.txt 2>&1
echo "finish parsing: $(date)" >> feeding_log.txt 2>&1

echo "start feeding: $(date)" >> feeding_log.txt 2>&1
python cli/cron_feeder.py >> feeding_log.txt 2>&1
echo "finish feeding: $(date)" >> feeding_log.txt 2>&1

echo "==========================================" >> feeding_log.txt
