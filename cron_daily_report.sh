#!/bin/bash

# add this script to cron:
# * 12 * * * /home/sgx_machine/datafeed_prod/datafeed-cli/cron_daily_report.sh > /home/sgx_machine/datafeed_prod/datafeed-cli/cron_log.txt

export PATH="$HOME/.cargo/bin:$PATH"
export PATH="/$HOME/.foundry/bin:$PATH"

cd datafeed_prod/datafeed-cli

source .env
source lib/sgx_verifier_deployer/.env

echo "start daily report: $(date)" >> daily_report_log.txt
python3 cli/telegram_notification.py >> daily_report_log.txt 2>&1
echo " finished daily report: $(date)" >> daily_report_log.txt

echo "==========================================" >> daily_report_log.txt
