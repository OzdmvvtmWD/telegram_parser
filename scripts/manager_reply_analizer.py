import re
import functools
import json
from settings.settings import mistal_api_key
from mistralai import Mistral
from datetime import date, datetime, timedelta
from scripts.metrics import Metrics
import logging

class ManagerAnalizer:
    
    def __init__(self,manager_id, data, model="mistral-small-latest"):
        # Initialize Mistral client and manager data
        self._api_key = mistal_api_key
        self._model = model
        self._client = Mistral(api_key=self._api_key)
        self._data = data
        self._manager_id = manager_id

        # Define available tool (function) for LLM
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

        # Bind tool name to actual method
        self._names_to_functions = {
            'get_all_dialogs': functools.partial(self.get_all_dialogs, self._data),
        }

    @staticmethod
    def get_all_dialogs(data):
        # Return all dialog data in JSON format
        return json.dumps(data, ensure_ascii=False)
    
    def make_analyz(self, mssgs):
        # Make initial LLM call with tool
        messages = mssgs
        response = self._client.chat.complete(
            model=self._model,
            messages=messages,
            tools=self._tools,
            tool_choice="any",
            parallel_tool_calls=False,
        )

        # Extract tool call and execute corresponding function
        tool_call = response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_params = json.loads(tool_call.function.arguments or "{}")

        function_result = self._names_to_functions[function_name](**function_params)

        # Append tool result to message history and run second completion
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


    def analyze_unfulfilled_promises(self):
        # Analyze if manager responded meaningfully by end of day
        messages = [
            {
                "role": "system",
                "content": "Ти аналізуєш діалоги менеджерів з клієнтами."
            },
            {
                "role": "user",
                "content": (
                    f"Проаналізуй кожен діалог із наведених. менеджер id {self._manager_id} "
                    "Знайди ті,  діалоги де менеджер не відповів клієнтам по сенсу до кінця дня, "
                    "Навіть якщо месседж про обіцянку прорахунку менеджера останній в діалозі з клієнтом."
                    "Результат подай у форматі JSON. Кожен запис має містити:\n"
                    "- ключ `dialog_id` — id діалогу;\n"
                    "- ключ `manager_responded` — чи менеджер відповів клієнтам по сенсу до кінця дня (True або False)\n"
                    "- ключ `reason` — коротке пояснення, чому діалог вважається проблемним;\n"
                    "- ключ `description` — короткий опис ситуації\n"
                    "Файл повинен починатися з `json`, формат повністю валідний, масивом обʼєктів з вищенаведеними полями."
                )
            }
        ]

        res = self.make_analyz(messages)
        json_reply = re.search(r"\[.*\]", res, re.DOTALL).group(0)
        dialogs = json.loads(json_reply)

        return dialogs


    def analyze_bad_replies(self):
        # Analyze toxic, cold, delayed, or otherwise poor manager replies
        messages = [
            {
                "role": "system",
                "content": "Ти аналізуєш діалоги менеджерів з клієнтами."
            },
            {
                "role": "user",
                "content" : (
                    "Проаналізуй усі надані діалоги та знайди ті, в яких спостерігається проблемна комунікація або негативна взаємодія між клієнтом \n"
                    f"і менеджером (id менеджера — {self._manager_id}). "
                    "До проблемної взаємодії належать такі ознаки:\n"
                    "- клієнт явно або неявно демонструє незадоволення, нетерпіння чи емоційний дискомфорт;\n"
                    "- менеджер не відповідає або відповідає не по суті, надто коротко, із запізненням, формально або байдуже;\n"
                    "- менеджер не ініціативний, клієнту доводиться 'витягувати' з нього відповіді;\n"
                    "- відсутність або недостатність консультації;\n"
                    "- грубість, ігнорування або сухість у спілкуванні.\n\n"
                    "Результат подай у форматі JSON. Кожен запис має містити:\n"
                    "- ключ `dialog_id` — id діалогу;\n"
                    "- ключ `reason` — коротке пояснення, чому діалог вважається проблемним;\n"
                    "- ключ `description` — короткий опис ситуації, яка свідчить про порушення або негативний накал.\n"

                    "Файл повинен починатися з `json`, формат повністю валідний, масивом обʼєктів з вищенаведеними полями."
                    "потім виводить самі розмови з проблемною взаємодєю"
                )
            }
        ]

        res = self.make_analyz(messages)
        json_reply = re.search(r"\[.*?\]", res, re.DOTALL) 

        try:
            dialogs = json.loads(json_reply.group(0))
            self.log_for_bad_replies(dialogs)
            return dialogs

        except json.JSONDecodeError as je:
            print(f"parse dialog error : {je}")


    def log_for_bad_replies(self, dialogs):
        # Log bad dialog results to file
        logger = logging.getLogger('bad_replies_logger')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler('bad_replies.log', mode='a', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        for dialog in dialogs:
            logger.info(dialog)

    def analyze_all_dialogs(self):
        # Run all quantitative metrics per dialog
        results = []

        for dialog in self._data:
            try:
                metrics = Metrics(self._manager_id,dialog)
                result = metrics.get_metric()
                result['dialog_id'] = dialog.get('dialog', {}).get('id', 'unknown')
                result['client_name'] = dialog.get('dialog', {}).get('name', 'unknown')
                results.append(result)
            except Exception as e:
                print(f"parse dialog error {dialog.get('dialog', {}).get('id', 'N/A')}: {e}")
        
        return results
