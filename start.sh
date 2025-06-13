#!/bin/bash

echo "Select an option:"
echo "1) Start Admin Approval Bot"
echo "2) Add New User Session"
echo "3) Start Forwarding Bot"

read -p "Enter choice [1-3]: " choice

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
    echo "Invalid option. Exiting."
    ;;
esac
