import logging

from pytz import timezone
from datetime import datetime, timedelta
from telethon import helpers, utils, hints, errors
from telethon.tl.types import User

# Class responsible for fetching dialogs and messages from Telegram using Telethon
class Reader:

    def __init__(self, client):
        # Store the Telethon client instance
        self._client = client

    @property
    def client(self):
        # Return the client (read-only property)
        return self._client

    # Asynchronously retrieve user dialogs from the past `days` up to `limit` users
    async def get_dialogs(self, limit: int, days: int):
        offset_date = datetime.now() - timedelta(days=days)
        offset_date = offset_date.astimezone(timezone('UTC'))  # Convert to UTC
        user_limit = limit

        try:
            # Iterate over all dialogs
            async for dialog in self.client.iter_dialogs():
                # Only consider private users (skip groups, channels, etc.)
                if not isinstance(dialog.entity, User):
                    continue

                # Skip old dialogs
                if dialog.date and dialog.date <= offset_date:
                    continue

                yield dialog  # Yield matching dialog
                user_limit -= 1

                if user_limit <= 0:
                    break  # Stop if limit reached

        except Exception as e:
            logging.warning(f"Error in get_dialogs method: {e}")

    # Asynchronously fetch messages from a specific chat, filtering by date
    async def get_messages(self, chat, limit: int, days: int):
        offset_date = datetime.now() - timedelta(days=days)
        offset_date = offset_date.astimezone(timezone('UTC'))

        try:
            # Iterate over messages in the given chat
            async for message in self.client.iter_messages(entity=chat, limit=limit):
                # Skip old messages
                if message.date and message.date <= offset_date:
                    continue

                yield message

        except Exception as e:
            logging.warning(f"Error in get_messages method: {e}")

    # Retrieve full message history for selected dialogs for further analysis
    async def get_all_messages_for_analysis(self, dialog_limit: int = 10, message_limit: int = 1000, dialog_days: int = 365, message_days: int = 30):
        results = []
        try:
            # Get recent dialogs
            async for dialog in self.get_dialogs(limit=dialog_limit, days=dialog_days):
                messages = []
                # Get recent messages for each dialog
                async for message in self.get_messages(chat=dialog.entity, limit=message_limit, days=message_days):
                    messages.append(self.message_data(message))

                # Store dialog and its messages (reversed to chronological order)
                results.append({
                    "dialog": self.dialog_data(dialog),
                    "messages": list(reversed(messages))
                })

        except Exception as e:
            logging.warning(f"Error in get_all_messages_for_emotion_analysis method: {e}")
        return results

    # Extract metadata from a dialog object
    def dialog_data(self, dialog):
        return {
            "id": dialog.id,
            "name": getattr(dialog, 'name', None),
            "entity_id": dialog.entity.id,
            "entity_username": getattr(dialog.entity, 'username', None),
        }

    # Extract relevant fields from a message object
    def message_data(self, message):
        return {
            "id": message.id,
            "date": message.date.isoformat() if message.date else None,
            "sender_id": message.sender_id,
            "text": message.text,
        }
