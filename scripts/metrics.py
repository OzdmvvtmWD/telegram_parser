from datetime import datetime
import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertForSequenceClassification

# Class for computing communication metrics for a specific manager in a dialog
class Metrics:
    def __init__(self, manager_id, data):
        self._manager_id = manager_id
        self._data = data
        self._messages = self._data['messages']

    # Count how many messages were sent by the manager
    def manager_replies_count(self):
        return len(self._manager_replies())

    # Count short replies (2 characters or fewer) from the manager
    def short_manager_replies_count(self):
        short_manager_replies_count = [reply for reply in self._manager_replies() if len(reply['text']) <= 2]
        return len(short_manager_replies_count)

    # Calculate average response time (in seconds) between client and manager messages
    def avg_reaction_time_sec(self):
        reaction_time_sec = self._reaction_time_sec()
        try:
            return sum(reaction_time_sec) / len(reaction_time_sec)
        except ZeroDivisionError:
            return 0.0

    # Return the longest response delay (in seconds) from manager to client
    def max_response_delay_sec(self):
        reaction_time_sec = self._reaction_time_sec()
        return max(reaction_time_sec) if reaction_time_sec else 0.0

    # Estimate the percentage of manager replies that are likely negative/toxic
    def manager_negative_percent(self):
        # Load pretrained Russian toxicity classifier model and tokenizer
        tokenizer = BertTokenizer.from_pretrained('s-nlp/russian_toxicity_classifier')
        model = BertForSequenceClassification.from_pretrained('s-nlp/russian_toxicity_classifier')
        model.eval()

        count = 0
        replies = self._manager_replies()
        for rpl in replies:
            inputs = tokenizer(rpl['text'], return_tensors='pt', truncation=True)
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = F.softmax(logits, dim=1)
                toxic_prob = probs[0][1].item()  # Probability of toxic class

            if toxic_prob > 0.7:
                count += 1

        try:
            return (count / len(replies)) * 100
        except ZeroDivisionError:
            return 0.0

    # Count how many client messages were ignored (not followed by a manager reply)
    def ignored_client_messages(self):
        ignored = 0
        for i, msg in enumerate(self._messages):
            if msg['sender_id'] == self._manager_id:
                continue

            found = False
            for next_msg in self._messages[i + 1:]:
                if next_msg["sender_id"] == self._manager_id:
                    found = True
                    break
            if not found:
                ignored += 1

        return ignored

    # Check if the manager initiated the conversation
    def manager_initiated(self):
        return self._messages[0]['sender_id'] == self._manager_id if self._messages else False

    # Count total number of messages in the dialog
    def total_messages(self):
        return len(self._messages)

    # Compute the ratio of manager messages to total messages (in %)
    def manager_message_ratio_percent(self):
        try:
            return (self.manager_replies_count() / self.total_messages()) * 100
        except ZeroDivisionError:
            return 0.0

    # Internal: Get a list of all messages from the manager
    def _manager_replies(self):
        return [reply for reply in self._messages if reply['sender_id'] == self._manager_id]

    # Internal: Calculate response times (in seconds) from client messages to manager replies
    def _reaction_time_sec(self):
        reaction_time_sec = []
        last_client = None

        for msg in self._messages:
            if msg['sender_id'] != self._manager_id:
                last_client = msg
                continue
            if not last_client:
                continue

            t1 = datetime.fromisoformat(last_client['date'])
            t2 = datetime.fromisoformat(msg['date'])
            delta = (t2 - t1).total_seconds()

            reaction_time_sec.append(delta)

        return reaction_time_sec

    # Public method: Return a dictionary of all computed metrics for the dialog
    def get_metric(self):
        metric = {}
        metric["avg_reaction_time_sec"] = self.avg_reaction_time_sec()
        metric["ignored_client_messages"] = self.ignored_client_messages()
        metric["manager_initiated"] = self.manager_initiated()
        metric["total_messages"] = self.total_messages()
        metric["max_response_delay_sec"] = self.max_response_delay_sec()
        metric["manager_message_ratio_percent"] = self.manager_message_ratio_percent()
        metric["manager_negative_percent"] = self.manager_negative_percent()
        return metric
