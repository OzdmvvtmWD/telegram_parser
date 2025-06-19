import logging
from telethon import TelegramClient
from settings.settings import username, api_id, api_hash

class Client(TelegramClient):
    def __init__(self):
        super().__init__(username, api_id, api_hash)

    async def start_client(self):
        try:
            await self.start() 
        except Exception as e:
            logging.warning(f"Error in start_client method: {e}")

