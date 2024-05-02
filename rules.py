import json
import sqlite3

from database import EmailDatabase
from gmail_api import GmailAPI


class RulesProcessor:
    def __init__(self, gmail_api, email_db, rules_file='rules.json'):
        self.db = email_db or EmailDatabase()
        self.gmail_api = gmail_api or GmailAPI()
        with open(rules_file, 'r') as f:
            self.rules = json.load(f)

    def process_emails(self):
        emails = self.db.fetch_all_emails()
        for email in emails:
            email_data = {
                'id': email[0],
                'from': email[1],
                'subject': email[2],
                'date': email[3],
                'body': email[4]
            }
            self.apply_rules_to_email(email_data)

    def apply_rules_to_email(self, email):
        for rule in self.rules:
            if self.evaluate_rule(email, rule):
                self.perform_actions(email['id'], rule['actions'])
                # Optionally, you can stop processing rules after the first match
                # break

    def evaluate_rule(self, email, rule):
        if rule['predicate'] == 'all':
            return all(self.evaluate_condition(email, condition) for condition in rule['conditions'])
        elif rule['predicate'] == 'any':
            return any(self.evaluate_condition(email, condition) for condition in rule['conditions'])

    @staticmethod
    def evaluate_condition(email, condition):
        field = condition['field']
        operator = condition['predicate']
        value = condition['value']
        email_value = email[field]

        if operator == 'contains':
            return value in email_value
        elif operator == 'not_contains':  # Assuming you meant "not_contains"
            return value not in email_value
        elif operator == 'equals':
            return value == email_value
        elif operator == 'not_equals':
            return value != email_value
        # ... (Add more operators as needed)

    def perform_actions(self, message_id, actions):
        for action in actions:
            if action['action'] == 'mark_as_read':
                self.gmail_api.mark_as_read(message_id)
            elif action['action'] == 'mark_as_unread':
                self.gmail_api.mark_as_unread(message_id)
            elif action['action'] == 'move_to_label':
                label_id = self.gmail_api.get_label_id(action['label'])
                if label_id:
                    self.gmail_api.move_to_label(message_id, label_id)

