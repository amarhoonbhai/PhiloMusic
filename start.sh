#!/bin/bash

choice=$1

if [ -z "$choice" ]; then
  echo "Usage: ./start.sh [1|2|3]"
  echo "1) Start Admin Approval Bot"
  echo "2) Add New User Session"
  echo "3) Start Forwarding Bot"
  exit 1
fi

case $choice in
  1)
    echo "Starting Admin Bot..."
    python3 admin_bot.py
    ;;
  2)
    echo "Starting User Session Adder..."
    python3 userbot.py
    ;;
  3)
    echo "Starting Forwarding Bot..."
    python3 userbot.py
    ;;
  *)
    echo "Invalid option. Use 1, 2, or 3."
    ;;
esac
