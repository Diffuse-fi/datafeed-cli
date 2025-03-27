from datetime import datetime, timedelta
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
            send_message(net, file_error = "unable to open log file " + logfile)

def daily_report():

    # report_day = datetime.today()
    report_day = datetime.today() - timedelta(days=1)
    date_str = report_day.strftime("%Y-%m-%d")

    health_report = f"health_report {date_str}:\n"
    gas_report = f"gas_report {date_str}:\n"
    token_report = f"token_report {date_str}:\n"
    balance_report = f"balance_report {date_str}:\n"
    budget_report = f"budget_report {date_str}:\n"
    money_report = f"money_report {date_str}:\n"
    total_money_spent = 0

    logs_list = []

    with open('logs/logs_list.txt', 'r') as file:
        for line in file:
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
                break

            if log.find("SUCCEEDED") == -1:
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
            days_until_out_of_money = int(balance / tokens_spent)
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

    final_report =  health_report + "\n\n" + money_report + "\n\n" + budget_report + "\n\n" + gas_report + "\n\n" + token_report + "\n\n" + balance_report + "\n\n"

    send_message(final_report)

def main():
    daily_report()

if __name__ == "__main__":
    main()
