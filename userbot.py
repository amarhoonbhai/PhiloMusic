
import os
import json
from datetime import datetime
import asyncio
from telethon import TelegramClient, events
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
OWNER_ID = 123456789  # Replace with your own Telegram user ID

SESSION_DIR = 'sessions'
GROUPS_FILE = 'groups.txt'
APPROVED_FILE = 'approved_users.json'
INTERVAL_MINUTES = 15

os.makedirs(SESSION_DIR, exist_ok=True)

def load_approved():
    try:
        with open(APPROVED_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def is_user_approved(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    approved = load_approved()
    expiry = approved.get(str(user_id))
    if not expiry:
        return False
    return datetime.utcnow().date() <= datetime.strptime(expiry, "%Y-%m-%d").date()

def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return set()
    with open(GROUPS_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_group(group_id):
    groups = load_groups()
    if group_id not in groups:
        with open(GROUPS_FILE, 'a') as f:
            f.write(f"{group_id}\n")
        print(f"Added new group: {group_id}")

async def add_user():
    phone = input("Enter your phone number: ")
    temp_client = TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH)
    await temp_client.connect()
    me = await temp_client.get_me()

    if not is_user_approved(me.id):
        print("❌ You are not approved to use this bot. Contact admin.")
        await temp_client.disconnect()
        return

    await temp_client.start(phone)
    print(f"✅ {me.id} logged in and session saved.")
    await temp_client.disconnect()

async def forward_from_saved():
    group_ids = list(load_groups())

    for session_file in os.listdir(SESSION_DIR):
        session_path = os.path.join(SESSION_DIR, session_file)
        client = TelegramClient(session_path, API_ID, API_HASH)
        await client.connect()

        if not await client.is_user_authorized():
            print(f"Session {session_file} not authorized. Skipping.")
            continue

        try:
            me = await client.get_me()
            if not is_user_approved(me.id):
                print(f"User {me.id} not approved or expired. Skipping.")
                continue

            messages = await client.get_messages('me', limit=1)
            if not messages:
                print(f"No saved messages for {me.id}")
                continue

            latest_msg = messages[0]
            for group_id in group_ids:
                try:
                    await client.send_message(int(group_id), latest_msg)
                    print(f"[{me.id}] → {group_id}")
                except Exception as e:
                    print(f"Failed to send to {group_id}: {e}")

        finally:
            await client.disconnect()

async def listen_for_groups():
    print("🔄 Listening for forwarded group messages to add groups...")
    client = TelegramClient("listener", API_ID, API_HASH)
    await client.start()

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if not event.fwd_from or not event.is_private:
            return

        user = await event.get_sender()
        if not is_user_approved(user.id):
            await event.reply("❌ You are not approved to use this bot.")
            return

        fwd = event.fwd_from
        if hasattr(fwd.from_id, 'channel_id'):
            group_id = fwd.from_id.channel_id
            save_group(str(group_id))
            await event.reply(f"✅ Group {group_id} added.")
        else:
            await event.reply("⚠️ Couldn't extract group ID.")

    await client.run_until_disconnected()

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(forward_from_saved, 'interval', minutes=INTERVAL_MINUTES)
    scheduler.start()
    await asyncio.gather(
        listen_for_groups()
    )

if __name__ == "__main__":
    print("1. Add user session")
    print("2. Start bot")

    choice = input("Choose option: ")
    if choice == '1':
        asyncio.run(add_user())
    elif choice == '2':
        asyncio.run(main())
    else:
        print("Invalid choice.")
