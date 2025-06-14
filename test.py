import functools
import pandas as pd
import json
from settings import mistal_api_key
from mistralai import Mistral

data = [
  {
  "dialog": {
    "id": 123456789,
    "name": "Олександр Коваль",
    "entity_id": 123456789,
    "entity_username": "koval_oleksandr"
  },
  "messages": [
    {
      "id": 301001,
      "date": "2025-06-13T09:12:10+00:00",
      
      "sender_id": 123456789,
      "text": "Доброго ранку! Хочу дізнатись статус замовлення."
    },
    {
      "id": 301002,
      "date": "2025-06-13T09:15:43+00:00",
      "sender_id": 123456789,
      "text": "Чи буде сьогодні відправка?"
    },
    {
      "id": 301003,
      "date": "2025-06-13T14:33:19+00:00",
      "sender_id": 123456789,
      "text": "Будь ласка, дайте відповідь сьогодні, бо це терміново."
    },
    {
      "id": 301004,
      "date": "2025-06-14T10:02:07+00:00",
      "sender_id": 953272656,
      "text": "Вибачте за затримку, ваше замовлення в обробці, сьогодні відправимо."
    }
  ]
},
  {
    "dialog": {
      "id": 793191982,
      "name": "Вадим Булавін",
      "entity_id": 793191982,
      "entity_username": "Xxxvadik"
    },
    "messages": [
      {
        "id": 213543,
        "date": "2025-06-14T18:12:47+00:00",
        "sender_id": 953272656,
      "text": "Доброго ранку! Хочу дізнатись статус замовлення."
      },
      {
        "id": 213537,
        "date": "2025-06-14T11:14:34+00:00",
        "sender_id": 953272656,
      "text": "ок"
      },
      {
        "id": 213296,
        "date": "2025-06-11T08:30:32+00:00",
        "sender_id": 953272656,
      "text": "Будь ласка, дайте відповідь сьогодні, бо це терміново."
      },
      {
        "id": 213294,
        "date": "2025-06-11T08:28:41+00:00",
        "sender_id": 953272656,
        "text": "угу"
      }
     
    ]
  }
  
]

from manager_reply_analizer import ManagerAnalizer

m = ManagerAnalizer(data)
print(m.analyze_unfulfilled_promises())
print(m.analyze_bad_replies())

# def get_all_dialogs(data):
#     return json.dumps(data, ensure_ascii=False)

# tools = [{
#     "type": "function",
#     "function": {
#         "name": "get_all_dialogs",
#         "description": "Return all dialogs from dataset",
#         "parameters": {
#             "type": "object",
#             "properties": {}
#         }
#     }
# }]

# names_to_functions = {
#     'get_all_dialogs': functools.partial(get_all_dialogs, data),
# }
# messages = [
#     {
#         "role": "system",
#         "content": "Ти аналізуєш діалоги менеджерів з клієнтами."
#     },
#     {
#         "role": "user",
#         "content": "Знайди діалог, де менеджер не відповів клієнтам по сенсу до кінця дня."
#     },
#     {
#         "role": "user",
#         "content": "Відповідь надішли JSON з id діалогу та повідомлень."
#     },
   
# ]

# client = Mistral(api_key=api_key)

# response = client.chat.complete(
#     model = model,
#     messages = messages,
#     tools = tools,
#     tool_choice = "any",
#     parallel_tool_calls = False,
# )

# tool_call = response.choices[0].message.tool_calls[0]
# function_name = tool_call.function.name
# function_params = json.loads(tool_call.function.arguments)

# function_result = names_to_functions[function_name](**function_params)

# messages.append({
#     "role":"user", 
#     "name":function_name, 
#     "content":function_result, 
#     "tool_call_id":tool_call.id
# })

# response = client.chat.complete(
#     model = model, 
#     messages = messages
# )

# result = response.choices[0].message.content
# result = response.choices[1].message.content

# print(result)
