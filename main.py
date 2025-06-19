import asyncio
from scripts.to_exel import json_to_exel_parse
from scripts.reader import Reader
from settings.client import Client
from scripts.manager_reply_analizer import ManagerAnalizer
from test_data import data  # Sample test data (can be used for testing instead of fetching real dialogs)

# Main asynchronous entry point
async def main():
    # Initialize and start the Telegram client
    client = Client()
    await client.start_client()

    # Get current authenticated manager's (user's) Telegram info
    manager = await client.get_me()

    # Initialize the Reader to fetch dialogs and messages
    reader = Reader(client)

    # Retrieve recent dialogs and messages for analysis
    dialogs = await reader.get_all_messages_for_analysis(
        dialog_limit=3,        # max number of dialogs
        dialog_days=365,        # fetch dialogs from last 365 days
        message_days=5,         # fetch messages from last 5 days
        message_limit=100       # max number of messages per dialog
    )

    # Create an analyzer for the current manager
    manager_analyz = ManagerAnalizer(manager.id, dialogs)

    print(len(dialogs))  # Print how many dialogs were fetched

    # Perform various types of analysis
    analyze_unfulfilled_promises = manager_analyz.analyze_unfulfilled_promises()
    analyze_bad_replies = manager_analyz.analyze_bad_replies()
    analyze_all_dialogs = manager_analyz.analyze_all_dialogs()

    # Output the results
    print('analyze_unfulfilled_promises')
    print("="*50)
    print(analyze_unfulfilled_promises)
    print("="*50)
    print(len(analyze_unfulfilled_promises))
    print("="*50)

    print('analyze_bad_replies')
    print(analyze_bad_replies)
    print("="*50)
    print(len(analyze_bad_replies))
    print("="*50)

    print('analyze_all_dialogs')
    print(analyze_all_dialogs)
    print("="*50)
    json_to_exel_parse(analyze_unfulfilled_promises, 'analyze_unfulfilled_promises')
    json_to_exel_parse(analyze_bad_replies, 'analyze_bad_replies')
    json_to_exel_parse(analyze_all_dialogs, 'analyze_all_dialogs')


    # Properly disconnect the Telegram client
    await client.disconnect()

# Entry point of the script
if __name__ == "__main__":
    asyncio.run(main())
