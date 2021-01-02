#!/bin/bash

# Set up crone for this script.
# Run command "crontab -e"
# append to the end:"
# SHELL=/bin/bash
# MAILTO=root@example.com
# */1 * * * * sh /root/moneybot/bot_autostart.sh
# " done :)

script_path="/root/moneybot/app.py"

if [ $(ps -ef | grep python3 | wc -l) -ne 3 ]
then
pkill -f python3
nohup python3 $script_path &
fi
