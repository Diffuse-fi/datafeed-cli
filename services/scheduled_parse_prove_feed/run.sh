#!/usr/bin/env bash

sudo mkdir -p /var/log/diffuse

sudo cp diffuse-parse-proove-feed.service /etc/systemd/system/
sudo cp diffuse-parse-proove-feed.timer   /etc/systemd/system/

sudo chmod +x PUT_YOUR_ABSOLUT_PATH_TO_DATAFEED_CLI_HERE/services/scheduled_parse_prove_feed/parse_and_prove_feed.sh

sudo systemctl daemon-reload

sudo systemctl enable diffuse-parse-proove-feed.timer
sudo systemctl start diffuse-parse-proove-feed.timer

echo "System-wide service and timer have been installed and started (running under root)."
echo "Check status via: sudo systemctl status diffuse-parse-proove-feed.timer"
echo "Logs will be written to: /var/log/diffuse/parse_and_prove_feed.log"
