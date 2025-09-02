#!/usr/bin/env bash

systemctl stop diffuse-parse-proove-feed.timer
systemctl disable diffuse-parse-proove-feed.timer

systemctl stop diffuse-parse-proove-feed.service
systemctl disable diffuse-parse-proove-feed.service

echo "Timer and service 'diffuse-parse-proove-feed' have been stopped and disabled."
echo "You can verify via: systemctl status diffuse-parse-proove-feed.timer"
