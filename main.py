import asyncio
from reader import Reader
from client import Client

import asyncio

async def main():
    client = Client()
    await client.start_client()
    reader = Reader(client)
    
    dialogs = await reader.get_all_messages_for_analysis(dialog_limit=10, dialog_days=365, message_days= 5, message_limit=100)
    print(dialogs[2]['messages'])
   
    await client.disconnect()  

if __name__ == "__main__":
    asyncio.run(main())