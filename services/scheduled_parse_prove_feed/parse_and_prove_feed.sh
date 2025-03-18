#!/usr/bin/env bash

mkdir -p /var/log/diffuse

echo "$(date) start feeding" >> /var/log/diffuse/parse_and_prove_feed.log

python3  cli/parse_prove_feed.py PUT_YOUR_CLI_PARAMETERS_HERE >> /var/log/diffuse/parse_and_prove_feed.log 2>&1

echo "$(date) data request and proving finished: " >> /var/log/diffuse/parse_and_prove_feed.log