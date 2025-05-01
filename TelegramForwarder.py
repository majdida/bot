import asyncio
from telethon.sync import TelegramClient
from telethon import errors

# 🔒 Hardcoded Telegram credentials
API_ID = 28373863  # Replace with your actual API ID (as an integer)
API_HASH = "a2943e3677b44f8c8eae56ba65756e12"  # Replace with your actual API Hash
PHONE_NUMBER = "+96181573356"  # Replace with your phone number including country code

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    async def list_chats(self):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input('Enter the code: '))
            except errors.rpcerrorlist.SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Enter your password: ')
                await self.client.sign_in(password=password)

        dialogs = await self.client.get_dialogs()
        with open(f"chats_of_{self.phone_number}.txt", "w", encoding="utf-8") as chats_file:
            for dialog in dialogs:
                print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
                chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")

        print("List of groups printed successfully!")

    async def forward_messages_to_channel(self, source_chat_id, destination_channel_id, keywords):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        last_message_id = (await self.client.get_messages(source_chat_id, limit=1))[0].id

        while True:
            print("Checking for messages and forwarding them...")
            messages = await self.client.get_messages(source_chat_id, min_id=last_message_id, limit=None)

            for message in reversed(messages):
                if keywords:
                    if message.text and any(keyword.strip().lower() in message.text.lower() for keyword in keywords):
                        print(f"Message contains a keyword: {message.text}")
                        await self.client.send_message(destination_channel_id, message.text)
                        print("Message forwarded")
                else:
                    await self.client.send_message(destination_channel_id, message.text)
                    print("Message forwarded")

                last_message_id = max(last_message_id, message.id)

            await asyncio.sleep(5)

async def main():
    forwarder = TelegramForwarder(API_ID, API_HASH, PHONE_NUMBER)

    print("Choose an option:")
    print("1. List Chats")
    print("2. Forward Messages")

    choice = input("Enter your choice: ")

    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        source_chat_id = int(input("Enter the source chat ID: "))
        destination_channel_id = int(input("Enter the destination chat ID: "))
        print("Enter keywords if you want to forward messages with specific keywords, or leave blank to forward every message!")
        keywords = input("Put keywords (comma separated if multiple, or leave blank): ").split(",")
        await forwarder.forward_messages_to_channel(source_chat_id, destination_channel_id, keywords)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
