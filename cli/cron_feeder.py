from datetime import datetime
import os
from feed_feeder import feed_data
from telegram_notification import notify_health_problem
from lib.sgx_verifier_deployer.script.utils.network import *


def main():
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open("logs/logs_list.txt", 'a') as logs_list:
        logs_list.write(current_time + "\n")

    for net in networks:
        if net == LOCAL_NETWORK:
            continue
        res = feed_data(net, True, False)
        with open("logs/" + net.dirname + current_time + ".txt", "w") as file:
            file.write(res)

    notify_health_problem(current_time)

main()