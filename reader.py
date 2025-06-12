import logging

from datetime import datetime, timedelta
from telethon import helpers, utils, hints, errors
from telethon.tl.types import User

class Reader:

    def __init__(self,client):
        self._client = client

    @property
    def client(self):
        return self._client

    async def get_dialogs(self, limit: int , days: int ):
        offset_date = datetime.now() - timedelta(days = days)
        user_limit = 0

        try:

            async for dialog in self.client.iter_dialogs(
                limit = limit,
                offset_date = offset_date, 
                ):
                if isinstance(dialog.entity, User):
                    yield dialog
                    user_limit +=1 

                    if user_limit >= limit:
                        break
        except Exception as e:
            logging.warning(f"Error in get_dialogs method: {e}")
    

    async def get_messages(self, chat, limit: int , days: int ):
        offset_date = datetime.now() - timedelta(days = days)
        try:
            async for message in self.client.iter_messages(
                entity = chat,
                limit = limit,
                offset_date = offset_date):
                yield message
        except Exception as e:
            logging.warning(f"Error in get_messages method: {e}")

    async def get_all_messages_for_emotion_analysis(self, dialog_limit: int = 10, message_limit: int = 10, dialog_days: int = 365, message_days: int = 30):
        results = []
        try:
            async for dialog in self.get_dialogs(limit=dialog_limit, days=dialog_days):
                messages = []
                async for message in self.get_messages(chat=dialog.entity, limit=message_limit, days=message_days):
                    messages.append(message)
                results.append([dialog, messages])

        except Exception as e:
            logging.warning(f"Error in get_all_messages_for_emotion_analysis method: {e}")
        return results
        
