import logging

from pytz import timezone
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
        offset_date = offset_date.astimezone(timezone('UTC'))
        user_limit = limit

        try:

            async for dialog in self.client.iter_dialogs():
                if not isinstance(dialog.entity, User):
                    continue

                if dialog.date and dialog.date <= offset_date:
                    continue 

                yield dialog
                user_limit -= 1

                if user_limit <= 0:
                    break

        except Exception as e:
            logging.warning(f"Error in get_dialogs method: {e}")
    

    async def get_messages(self, chat, limit: int , days: int ):
        offset_date = datetime.now() - timedelta(days = days)
        offset_date = offset_date.astimezone(timezone('UTC'))

        try:
            async for message in self.client.iter_messages(entity = chat, limit = limit):
                if message.date and message.date <= offset_date:
                    continue
                
                yield message

        except Exception as e:
            logging.warning(f"Error in get_messages method: {e}")

    async def get_all_messages_for_analysis(self, dialog_limit: int = 10, message_limit: int = 1000, dialog_days: int = 365, message_days: int = 30):
        results = []
        try:
            async for dialog in self.get_dialogs(limit=dialog_limit, days=dialog_days):
                messages = []
                async for message in self.get_messages(chat=dialog.entity, limit=message_limit, days=message_days):
                    messages.append(self.message_data(message))
                
                results.append(
                   {
                    "dialog": self.dialog_data(dialog),
                    "messages": messages
                    })

        except Exception as e:
            logging.warning(f"Error in get_all_messages_for_emotion_analysis method: {e}")
        return results
    

    def dialog_data(self, dialog):
        return  {
                "id": dialog.id,
                "name": getattr(dialog, 'name', None),
                "entity_id": dialog.entity.id,
                "entity_username": getattr(dialog.entity, 'username', None),
            }
    
    def message_data(self, message):
        return  {
                    "id": message.id,
                    "date": message.date.isoformat() if message.date else None,
                    "sender_id": message.sender_id,
                    "text": message.text,
                }


