import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from database import EmailDatabase
from rules import RulesProcessor
from gmail_api import GmailAPI


class TestRulesProcessor(unittest.TestCase):
    def setUp(self):
        self.mock_email_db = MagicMock(spec=EmailDatabase)
        self.mock_gmail_api = MagicMock(spec=GmailAPI)  # Mock GmailAPI for testing
        self.rules_processor = RulesProcessor(self.mock_gmail_api, self.mock_email_db)

    def _mock_emails(self, emails):
        self.mock_email_db.fetch_all_emails.return_value = emails

    @patch.object(RulesProcessor, '_evaluate_condition')
    def test_evaluate_rule_all_true(self, mock_evaluate_condition):
        mock_evaluate_condition.side_effect = [True, True, True]
        rule = {'predicate': 'all', 'conditions': [{}, {}, {}]}
        result = self.rules_processor._evaluate_rule({'id': '1'}, rule)
        self.assertTrue(result)
        mock_evaluate_condition.assert_has_calls([
            unittest.mock.call({'id': '1'}, {}),
            unittest.mock.call({'id': '1'}, {}),
            unittest.mock.call({'id': '1'}, {})
        ])

    @patch.object(RulesProcessor, '_evaluate_condition')
    def test_evaluate_rule_any_true(self, mock_evaluate_condition):
        mock_evaluate_condition.side_effect = [False, True, False]
        rule = {'predicate': 'any', 'conditions': [{}, {}, {}]}
        result = self.rules_processor._evaluate_rule({'id': '1'}, rule)
        self.assertTrue(result)

    def test_evaluate_rule_invalid_predicate(self):
        rule = {'predicate': 'invalid', 'conditions': []}
        with self.assertRaises(ValueError):
            self.rules_processor._evaluate_rule({'id': '1'}, rule)

    def test_evaluate_condition_contains(self):
        condition = {'field': 'subject', 'predicate': 'contains', 'value': 'promo'}
        result = self.rules_processor._evaluate_condition({'subject': 'Summer Promotion'}, condition)
        self.assertTrue(result)

    def test_evaluate_condition_date_less_than(self):
        condition = {'field': 'date', 'predicate': 'less_than', 'value': '5'}
        past_date = (datetime.now() - timedelta(days=6)).isoformat()
        result = self.rules_processor._evaluate_condition({'date': past_date}, condition)
        self.assertTrue(result)

    def test_evaluate_condition_invalid_operator(self):
        condition = {'field': 'subject', 'predicate': 'invalid', 'value': 'promo'}
        with self.assertRaises(ValueError):
            self.rules_processor._evaluate_condition({'subject': 'Summer Promotion'}, condition)

    def test_perform_actions_mark_as_read(self):
        actions = [{'action': 'mark_as_read'}]
        self.rules_processor._perform_actions('msg123', actions)
        self.mock_gmail_api.mark_as_read.assert_called_once_with('msg123')

    def test_perform_actions_move_to_label_not_found(self):
        self.mock_gmail_api.get_label_id.return_value = None
        actions = [{'action': 'move_to_label', 'label': 'NonExistentLabel'}]
        self.rules_processor._perform_actions('msg123', actions)
        self.mock_gmail_api.move_to_label.assert_not_called()  # Ensure move_to_label is not called

    def test_perform_actions_invalid_action(self):
        actions = [{'action': 'invalid'}]
        with self.assertRaises(ValueError):
            self.rules_processor._perform_actions('msg123', actions)

    @patch.object(RulesProcessor, '_apply_rules_to_email')
    def test_process_emails(self, mock_apply_rules):
        emails = [{'id': '1'}, {'id': '2'}]
        self._mock_emails(emails)
        self.rules_processor.process_emails()
        mock_apply_rules.assert_has_calls([
            unittest.mock.call({'id': '1'}),
            unittest.mock.call({'id': '2'})
        ])
