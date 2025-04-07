from datetime import datetime, timedelta
import argparse
import subprocess
import os
import telebot
from lib.sgx_verifier_deployer.script.utils.network import *


def send_message(msg):
    TOKEN = os.getenv("TELEBOT_TOKEN")
    chatID = os.getenv("CHAT_ID")
    chatID = int(chatID)

    bot = telebot.TeleBot(TOKEN)
    bot.send_message(chatID, msg, disable_notification=True)


def notify_health_problem(current_time):
    for net in networks:
        if net == LOCAL_NETWORK:
            continue

        logfile = "logs/" + net.dirname + current_time + ".txt"
        try:
            file = open(logfile)
            log = file.read()
            file.close()
            if "FAILED!" in log:
                fail_msg = "🚨🆘 FEEDING FAILED 🆘🚨\n"
                msg = fail_msg + "newtork: " + net.name + "\nlogs:\n" + log
                send_message(msg)
        except:
            send_message("unable to open log file " + logfile)


def report_for_last_days(days):

    date_strings = []

    for i in range(days):
        report_day = datetime.today() - timedelta(days=1) - timedelta(days=i)
        date_str = report_day.strftime("%Y-%m-%d")
        date_strings.append(date_str)

    if len(date_strings) == 1:
        report_peirod = date_strings[0]
    else:
        report_peirod = date_strings[-1] + " — " + date_strings[0]

    health_report = f"health_report {report_peirod}:\n"
    gas_report = f"gas_report {report_peirod}:\n"
    token_report = f"token_report {report_peirod}:\n"
    balance_report = f"balance_report {report_peirod}:\n"
    budget_report = f"budget_report {report_peirod}:\n"
    money_report = f"money_report {report_peirod}:\n"
    total_money_spent = 0

    logs_list = []

    with open('logs/logs_list.txt', 'r') as file:
        for line in file:
            for date_str in date_strings:
                if date_str in line:
                    logs_list.append(line.strip())

    for net in networks:
        if net == LOCAL_NETWORK:
            continue

        health = 0
        unhealth = 0
        gas_spent = 0
        tokens_spent = 0

        for l in logs_list:
            logname = "logs/" + net.dirname + l + ".txt"
            try:
                with open(logname, 'r') as logfile:
                    log = logfile.read()
            except:
                unhealth += 1
                continue

            if log.find("FAILED!") != -1:
                unhealth += 1
            else:
                health += 1
                gas_used =  int(log.split("gasUsed              ")[1].split("\n")[0])
                gas_price = int(log.split("effectiveGasPrice    ")[1].split("\n")[0])

                gas_spent += gas_used
                tokens_spent += (gas_used * gas_price)

        cmd = ['cast', 'balance', os.getenv("PUBLIC_KEY"), '--rpc-url=' + net.rpc_url]
        res = subprocess.run(cmd, capture_output=True, text=True)
        balance = int(res.stdout) / (10**18)


        rounds = health + unhealth
        uptime_percentage = health/rounds * 100
        millions_of_gas_spent = gas_spent / (10**6)
        tokens_spent = tokens_spent / (10 ** 18)
        try:
            days_until_out_of_money = int(balance / tokens_spent) * days
        except:
            days_until_out_of_money = "error"

        try:
            collapse_day = datetime.today() + timedelta(days=days_until_out_of_money)
            collapse_day = collapse_day.strftime("%Y-%m-%d")
        except:
            collapse_day = "error"


        health_report += f"{net.name}: {unhealth} rounds failed out of {rounds} rounds => {uptime_percentage:.3g}% uptime\n"
        gas_report += f"{net.name}: spent {millions_of_gas_spent:.3g} millions of gas\n"
        budget_report += f"{net.name}: out of money in {days_until_out_of_money} days ({collapse_day})\n"
        token_report += f"{net.name}: spent {tokens_spent:.3g} tokens\n"
        balance_report += f"{net.name}: {balance:.3g} tokens\n"

        if "mainnet" in net.name:
            if net == OPTIMISM_MAINNET or net == ARBITRUM_MAINNET or net == BASE_MAINNET:
                token_price = 2000
            if net == AVAX_MAINNET:
                token_price = 20
            if net == SONIC_MAINNET:
                token_price = 0.5
            if net == ATA_MAINNET:
                token_price == 0.06
            if net == BERACHAIN_MAINNET:
                token_price = 6
            money_spent = tokens_spent * token_price
            money_report += f"{net.name}: spent {money_spent:.3g} USD\n"

            total_money_spent += money_spent

    money_report += f"total amount spent on all chains: {total_money_spent:.3g} USD"

    final_report = ""
    if days == 1:
        final_report = "=== DIFFUSE DATAFEED DAILY REPORT ===\n\n"
    if days == 7:
        final_report = "=== DIFFUSE DATAFEED WEEKLY REPORT ===\n\n"

    final_report +=  health_report + "\n\n" + money_report + "\n\n" + budget_report + "\n\n" + gas_report + "\n\n" + token_report + "\n\n" + balance_report + "\n\n"

    send_message(final_report)


def bugs_report(days):

    date_strings = []

    for i in range(days):
        report_day = datetime.today() - timedelta(days=1) - timedelta(days=i)
        date_str = report_day.strftime("%Y-%m-%d")
        date_strings.append(date_str)


    if len(date_strings) == 1:
        report_peirod = date_strings[0]
    else:
        report_peirod = date_strings[-1] + " — " + date_strings[0]

    bug_report = "=== DIFFUSE DATAFEED BUG REPORT ===\n\n"
    bug_report += "report_peirod:" + report_peirod + '\n'

    logs_list = []

    with open('logs/logs_list.txt', 'r') as file:
        for line in file:
            for date_str in date_strings:
                if date_str in line:
                    logs_list.append(line.strip())

    for net in networks:
        if net == LOCAL_NETWORK:
            continue

        for l in logs_list:
            logname = "logs/" + net.dirname + l + ".txt"
            try:
                with open(logname, 'r') as logfile:
                    log = logfile.read()
            except:
                continue

            if log.find("FAILED!") != -1:
                bug_report += logname + '\n'
                bug_report += log + '\n'

    send_message(bug_report)


def main(days):
    report_for_last_days(days)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Data feeder parameters")
    parser.add_argument('-d', '--days-amount', type=int, help="Report for how many days, default value 1")
    args = parser.parse_args()

    days = 1
    if args.days_amount is not None:
        days = args.days_amount

    main(days)
