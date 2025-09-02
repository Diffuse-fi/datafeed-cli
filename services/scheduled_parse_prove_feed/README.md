# Diffuse Datafeed (systemd service + timer)

This project allows you to schedule the `parse_and_prove_feed.sh` script using `systemd`. The script, in turn, runs the Python program `parse_prove_feed.py` with parameters from the `.env` file and writes logs to `/var/log/diffuse/parse_and_prove_feed.log`.

## Installation

1. Place the project files in the desired directory, for example: `~/datafeed-cli/`.
2. Create a `.env` file based on `.env-example` and fill in the required variables.
3. In the files `diffuse-parse-proove-feed.service` and `diffuse-parse-proove-feed.timer`, specify:
   - The absolute paths to the directory containing the scripts and `.env`.
   - If needed, adjust the timer frequency (by default, every 5 seconds).
4. In `parse_and_prove_feed.sh`, specify any parameters needed for `parse_prove_feed.py`.
5. Run the setup script:

```bash
chmod +x run.sh
./run.sh
```

This script copies the relevant files to the system directories, reloads `systemd`, and enables the timer.

## Checking Status

- To check the timer status:

```bash
sudo systemctl status diffuse-parse-proove-feed.timer
```

- To view logs:

```bash
tail -f /var/log/diffuse/parse_and_prove_feed.log
```

## Stopping

To stop the service and timer:

```bash
./stop.sh
```

This script will stop and disable both the service and the timer (check with `systemctl status diffuse-parse-proove-feed.timer`).

## Changing the Schedule

To change the run frequency, edit `OnUnitActiveSec` and other settings in `diffuse-parse-proove-feed.timer`, then run:

```bash
sudo systemctl daemon-reload
sudo systemctl restart diffuse-parse-proove-feed.timer
```

All logs will continue to be written to `/var/log/diffuse/parse_and_prove_feed.log`.
