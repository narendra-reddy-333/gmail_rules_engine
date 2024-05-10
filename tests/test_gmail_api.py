import unittest
from unittest.mock import patch

from gmail_api import GmailAPI


class TestGmailAPI(unittest.TestCase):
    def setUp(self):
        self.gmail_api = GmailAPI()

    @patch('gmail_api.GmailAPI.service')
    def test_get_label_id_found(self, mock_service):
        mock_service.users().labels().list.return_value.execute.return_value = {
            'labels': [
                {'id': '123', 'name': 'Important'},
                {'id': '456', 'name': 'Promotions'}
            ]
        }
        label_id = self.gmail_api.get_label_id('Important')
        self.assertEqual(label_id, '123')

    @patch('gmail_api.GmailAPI.service')
    def test_get_label_id_not_found(self, mock_service):
        mock_service.users().labels().list.return_value.execute.return_value = {
            'labels': [
                {'id': '123', 'name': 'Important'},
                {'id': '456', 'name': 'Promotions'}
            ]
        }
        label_id = self.gmail_api.get_label_id('NonExistentLabel')
        self.assertIsNone(label_id)

    @patch('gmail_api.GmailAPI.service')
    def test_get_label_id_empty_list(self, mock_service):
        mock_service.users().labels().list.return_value.execute.return_value = {
            'labels': []  # Empty list of labels
        }
        label_id = self.gmail_api.get_label_id('AnyLabel')
        self.assertIsNone(label_id)

    @patch('gmail_api.GmailAPI.service')
    def test_mark_as_read(self, mock_service):
        message_id = 'abc123'
        self.gmail_api.mark_as_read(message_id)
        mock_service.users().messages().modify.assert_called_once_with(
            userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}
        )

    @patch('gmail_api.GmailAPI.service')
    def test_mark_as_unread(self, mock_service):
        message_id = 'abc123'
        self.gmail_api.mark_as_unread(message_id)
        mock_service.users().messages().modify.assert_called_once_with(
            userId='me', id=message_id, body={'addLabelIds': ['UNREAD']}
        )

    @patch('gmail_api.GmailAPI.service')
    def test_move_to_label(self, mock_service):
        message_id = 'abc123'
        label_id = '456'
        self.gmail_api.move_to_label(message_id, label_id)
        mock_service.users().messages().modify.assert_called_once_with(
            userId='me', id=message_id, body={'addLabelIds': [label_id],
                                              'removeLabelIds': ['INBOX']})

    @patch('gmail_api.GmailAPI.service')
    def test_move_to_folder_trash(self, mock_service):
        message_id = 'abc123'
        self.gmail_api.move_to_folder(message_id, 'Trash')
        mock_service.users().messages().trash.assert_called_once_with(userId='me', id=message_id)

    @patch('gmail_api.GmailAPI.service')
    def test_move_to_folder_spam(self, mock_service):
        message_id = 'abc123'
        self.gmail_api.move_to_folder(message_id, 'Spam')
        mock_service.users().messages().trash.assert_called_once_with(userId='me', id=message_id)

    @patch('gmail_api.GmailAPI.service')
    def test_move_to_folder_inbox(self, mock_service):
        message_id = 'abc123'
        self.gmail_api.move_to_folder(message_id, 'Inbox')
        mock_service.users().messages().untrash.assert_called_once_with(userId='me', id=message_id)

    def test_move_to_folder_invalid(self):
        with self.assertRaises(ValueError):
            self.gmail_api.move_to_folder('abc123', 'InvalidFolder')
