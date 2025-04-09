from datetime import datetime
import os
from feed_feeder import feed_data, find_latest_data
from telegram_notification import notify_health_problem
from lib.sgx_verifier_deployer.script.utils.network import *


def main():
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open("logs/logs_list.txt", 'a') as logs_list:
        logs_list.write(current_time + "\n")

    # if feeding takes too long, next parse_and_prove starts and creates next dir in data/
    # and feeding fails because proof is not created yet, fixing data dir at the scart
    latest_data_dir="data/" + str(find_latest_data()) + "/"

    for net in networks:
        if net == LOCAL_NETWORK:
            continue
        try:
            res = feed_data(net, True, False, latest_data_dir)
        except Exception as e:
            res = "FAILED!\nException occured during feed_data execution: " + str(e)
        with open("logs/" + net.dirname + current_time + ".txt", "w") as file:
            file.write(res)

    notify_health_problem(current_time)

main()