import json
from datetime import datetime, timedelta

from database import EmailDatabase
from gmail_api import GmailAPI


class RulesProcessor:
    def __init__(self, gmail_api=None, email_db=None, rules_file='rules.json'):
        self.db = email_db or EmailDatabase()
        self.gmail_api = gmail_api or GmailAPI()
        with open(rules_file, 'r') as f:
            self.rules = json.load(f)

    def process_emails(self):
        emails = self.db.fetch_all_emails()
        for email in emails:
            self._apply_rules_to_email(email)

    def _apply_rules_to_email(self, email_data):
        for rule in self.rules:
            if self._evaluate_rule(email_data, rule):
                self._perform_actions(email_data['id'], rule['actions'])
                # Optionally, break here if you only want to apply the first matching rule

    def _evaluate_rule(self, email, rule):
        if rule['predicate'] == 'all':
            return all(self._evaluate_condition(email, cond) for cond in rule['conditions'])
        elif rule['predicate'] == 'any':
            return any(self._evaluate_condition(email, cond) for cond in rule['conditions'])
        else:
            raise ValueError("Invalid rule predicate: " + rule['predicate'])

    @staticmethod
    def _evaluate_condition(email, condition):
        field, operator, value = condition['field'], condition['predicate'], condition['value']
        email_value = email[field]

        if operator == 'contains':
            return value in email_value
        elif operator == 'not_contains':
            return value not in email_value
        elif operator == 'equals':
            return value == email_value
        elif operator == 'not_equals':
            return value != email_value
        elif field == 'date':
            try:
                email_date = datetime.fromisoformat(email_value)
                if operator == 'less_than':
                    comparison_date = datetime.now() - timedelta(days=int(value))
                    return email_date < comparison_date
                elif operator == 'greater_than':
                    comparison_date = datetime.now() + timedelta(days=int(value))
                    return email_date > comparison_date
                else:
                    raise ValueError("Invalid date comparison operator: " + operator)
            except ValueError:
                # Handle invalid date format
                return False
        else:
            raise ValueError("Invalid condition operator: " + operator)

    def _perform_actions(self, message_id, actions):
        for action in actions:
            action_type = action['action']
            if action_type == 'mark_as_read':
                self.gmail_api.mark_as_read(message_id)
            elif action_type == 'mark_as_unread':
                self.gmail_api.mark_as_unread(message_id)
            elif action_type == 'move_to_label':
                label_id = self.gmail_api.get_label_id(action['label'])
                if label_id:
                    self.gmail_api.move_to_label(message_id, label_id)
                else:
                    print(f"Label not found: {action['label']}")  # Or handle it differently
            elif action_type == 'move_to_folder':
                self.gmail_api.move_to_folder(message_id, action['folder'])
            else:
                raise ValueError("Invalid action type: " + action_type)
