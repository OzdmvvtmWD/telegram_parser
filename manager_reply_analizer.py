import functools
import json
from settings import mistal_api_key
from mistralai import Mistral

class ManagerAnalizer:
    
    def __init__(self, data, model="mistral-small-latest"):
        self._api_key = mistal_api_key
        self._model = model
        self._client = Mistral(api_key=self._api_key)
        self._data = data

        self._tools = [{
            "type": "function",
            "function": {
                "name": "get_all_dialogs",
                "description": "Return all dialogs from dataset",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }]

        self._names_to_functions = {
            'get_all_dialogs': functools.partial(self.get_all_dialogs, self._data),
        }

    @staticmethod
    def get_all_dialogs(data):
        return json.dumps(data, ensure_ascii=False)

    def analyze_unfulfilled_promises(self):
        messages = [
            {
                "role": "system",
                "content": "Ти аналізуєш діалоги менеджерів з клієнтами."
            },
            {
                "role": "user",
                "content": (
                    "Проаналізуй кожен діалог із наведених. "
                    "Знайди ті, де менеджер пообіцяв відповісти або виконати дію до кінця дня, "
                    "але не виконав цього вчасно. Відповідь дай у форматі JSON, "
                    "де вказано id діалогу, чи була обіцянка, чи виконана вона, та короткий опис."
                )
            }
        ]

        response = self._client.chat.complete(
            model=self._model,
            messages=messages,
            tools=self._tools,
            tool_choice="any",
            parallel_tool_calls=False,
        )

        tool_call = response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_params = json.loads(tool_call.function.arguments or "{}")

        function_result = self._names_to_functions[function_name](**function_params)

        messages.append({
            "role": "user",
            "name": function_name,
            "content": function_result,
            "tool_call_id": tool_call.id
        })

        response = self._client.chat.complete(
            model=self._model,
            messages=messages
        )

        return response.choices[0].message.content

    def analyze_bad_replies(self):
      
        dialogs_text = ""
        for d in self._data:
            dialogs_text += f"Діалог id {d['dialog']['id']} між менеджером і клієнтом:\n"
            for msg in sorted(d['messages'], key=lambda x: x['date']):
                role = "Менеджер" if msg['sender_id'] != d['dialog']['entity_id'] else "Клієнт"
                dialogs_text += f"{role}: {msg['text']}\n"
            dialogs_text += "\n"

        messages = [
            {
                "role": "system",
                "content": "Ти аналізуєш діалоги менеджерів з клієнтами."
            },
            {
                "role": "user",
                "content": (
                    "Проаналізуй цей текст з кількома діалогами.\n"
                    "Визнач, чи є в них негатив, незадоволення клієнта, помилки менеджера, "
                    "пасивність менеджера або недостатня ініціатива.\n"
                    "Якщо є проблеми — відповідай 'YES', і наведи коротко які саме, інакше 'NO'.\n\n"
                    f"{dialogs_text}"
                )
            }
        ]

        response = self._client.chat.complete(
            model=self._model,
            messages=messages
        )
        return response.choices[0].message.content

