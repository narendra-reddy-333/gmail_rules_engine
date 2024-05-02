import unittest

from database import EmailDatabase


class TestEmailDatabase(unittest.TestCase):
    def setUp(self):
        self.db = EmailDatabase('test_emails.db')  # Use a test database

    def test_create_table(self):
        # Check if the table exists
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails'")
        self.assertIsNotNone(cursor.fetchone())

    def test_store_and_fetch_emails(self):
        test_emails = [
            {'id': '1', 'from': 'test1@example.com', 'subject': 'Test Email 1', 'date': '2023-11-01',
             'body': 'Test Body 1'},
            {'id': '2', 'from': 'test2@example.com', 'subject': 'Test Email 2', 'date': '2023-11-02',
             'body': 'Test Body 2'}
        ]
        self.db.store_emails(test_emails)
        fetched_emails = self.db.fetch_all_emails()
        self.assertEqual(len(fetched_emails), 2)
        # Compare individual email data...

    def tearDown(self):
        self.db.conn.close()
