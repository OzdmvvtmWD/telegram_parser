from sentence_transformers import SentenceTransformer, util
from datetime import datetime
import numpy as np
messages = [
    {
        "id": 1,
        "date": "2025-06-10T09:00:00+00:00",
        "sender_id": 1,
        "text": "Привіт, підкажіть, будь ласка, яка ціна на доставку?"
    },
    {
        "id": 2,
        "date": "2025-06-10T09:01:00+00:00",
        "sender_id": 2,
        "text": "Добрий день"
    },
    {
        "id": 3,
        "date": "2025-06-10T09:05:00+00:00",
        "sender_id": 1,
        "text": "Можна отримати рахунок на оплату?"
    },
    {
        "id": 4,
        "date": "2025-06-10T09:10:00+00:00",
        "sender_id": 2,
        "text": "Ок"
    },
    {
        "id": 5,
        "date": "2025-06-10T10:00:00+00:00",
        "sender_id": 1,
        "text": "А коли буде прорахунок?"
    },
    {
        "id": 6,
        "date": "2025-06-10T11:00:00+00:00",
        "sender_id": 2,
        "text": "Зроблю пізніше"
    },
    {
        "id": 7,
        "date": "2025-06-10T18:00:00+00:00",
        "sender_id": 1,
        "text": "Чекаю на прорахунок"
    },
    {
        "id": 8,
        "date": "2025-06-11T09:00:00+00:00",
        "sender_id": 2,
        "text": "Вже зробив прорахунок, ось файл"
    }
]

class SemanticResponder:
    def __init__(self, model_name='paraphrase-MiniLM-L6-v2', threshold=0.65):
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold

    def is_relevant(self, client_msg: str, manager_msg: str) -> bool:
        if not manager_msg.strip():
            return False
        embeddings = self.model.encode([client_msg, manager_msg])
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        return similarity.item() >= self.threshold

def find_irrelevant_or_no_response(messages, manager_id: int):
    responder = SemanticResponder()
    messages = sorted(messages, key=lambda m: m['date'])
    results = []

    for i, msg in enumerate(messages):
        if msg['sender_id'] == manager_id:
            continue  
        client_msg = msg['text'].strip()
        if not client_msg:
            continue

        response_found = False
        manager_response = None

        for next_msg in messages[i+1:]:
            if next_msg['sender_id'] == manager_id:
                manager_response = next_msg['text'].strip()
                if responder.is_relevant(client_msg, manager_response):
                    response_found = True
                break

        if not response_found:
            results.append({
                'client_date': msg['date'],
                'client_msg': client_msg,
                'manager_response': manager_response or '',
            })

    return results


unanswered = find_irrelevant_or_no_response(messages, manager_id=953272656)
for item in unanswered:
    print(f"[{item['client_date']}] Клієнт: {item['client_msg']}")
    print(f"↳ Відповідь менеджера: {item['manager_response'] or 'ВІДСУТНЯ'}\n")