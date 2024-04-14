# import pandas as pd
# from telethon.sync import TelegramClient
# import asyncio
# import time
# # Use your own values from my.telegram.org
# api_id = 26765027
# api_hash = '57b569449b63f1fb1497f517aabca429'
# phone = '+7 968 715 7011'

# chat_id = -4001359758

# # async def main():
# #     client = TelegramClient(phone, api_id, api_hash)
# #     await client.start()
# #     print(await client.get_me())

# # if __name__ == "__main__":
# #     asyncio.run(main())

# client:TelegramClient = TelegramClient('anon', api_id, api_hash)

# async def main():
#     while True:
#         await client.send_message(chat_id, '/Любой текст/')
#         time.sleep(60)


# with client:
#     client.loop.run_until_complete(main())