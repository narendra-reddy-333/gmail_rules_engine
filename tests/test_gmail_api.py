import unittest
from unittest.mock import patch

from gmail_api import GmailAPI


class TestGmailAPI(unittest.TestCase):
    def setUp(self):
        self.gmail_api = GmailAPI()  # Assuming you have valid credentials

    @patch('gmail_api.GmailAPI.service')
    def test_get_label_id(self, mock_service):
        # Mock the response from the labels.list() method
        mock_service.users().labels().list.return_value.execute.return_value = {
            'labels': [
                {'id': '123', 'name': 'Important'},
                {'id': '456', 'name': 'Promotions'}
            ]
        }
        label_id = self.gmail_api.get_label_id('Important')
        self.assertEqual(label_id, '123')

        label_id = self.gmail_api.get_label_id('NonExistentLabel')
        self.assertIsNone(label_id)
