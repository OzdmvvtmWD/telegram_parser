import asyncio
from reader import Reader
from client import Client

import asyncio

async def main():
    client = Client()
    await client.start_client()
    reader = Reader(client)
    
    dialogs = await reader.get_all_messages_for_emotion_analysis(dialog_limit=2,dialog_days=10)
    print(dialogs[0][0])
    
    await client.disconnect()  

if __name__ == "__main__":
    asyncio.run(main())