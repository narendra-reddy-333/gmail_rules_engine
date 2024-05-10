# ----------------------------------------
# TestEmailDatabase
# ----------------------------------------
import os
from unittest import TestCase

from database import EmailDatabase


class TestEmailDatabase(TestCase):
    def setUp(self):
        self.db_file = 'test_database.db'  # Use a separate test database
        self.email_db = EmailDatabase(self.db_file)

    def tearDown(self):
        # Clean up the test database
        os.remove(self.db_file)

    def test_create_table(self):
        # Check if the table exists
        cursor = self.email_db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails'")
        self.assertIsNotNone(cursor.fetchone())

        emails = [
            {'id': '1', 'from': 'sender1@example.com', 'subject': 'Subject 1', 'date': '2023-11-28', 'body': 'Body 1'},
            {'id': '2', 'from': 'sender2@example.com', 'subject': 'Subject 2', 'date': '2023-11-27', 'body': 'Body 2'}
        ]
        self.email_db.store_emails(emails)

        cursor = self.email_db.conn.cursor()
        cursor.execute("SELECT * FROM emails")
        fetched_emails = cursor.fetchall()
        self.assertEqual(len(fetched_emails), 2)

        # Check details of each email
        for i, email in enumerate(emails):
            fetched_email = fetched_emails[i]
            self.assertEqual(fetched_email[0], email['id'])  # Check ID
            self.assertEqual(fetched_email[1], email['from'])  # Check sender
            self.assertEqual(fetched_email[2], email['subject'])  # Check subject
            self.assertEqual(fetched_email[3], email['date'])  # Check date
            self.assertEqual(fetched_email[4], email['body'])  # Check body

    def test_fetch_all_emails(self):
        test_emails = [
            {'id': '101', 'from': 'test1@example.com', 'subject': 'Test Email 1', 'date': '2023-11-29',
             'body': 'Test Body 1'},
            {'id': '102', 'from': 'test2@example.com', 'subject': 'Test Email 2', 'date': '2023-11-28',
             'body': 'Test Body 2'}
        ]
        self.email_db.store_emails(test_emails)  # Insert test emails

        fetched_emails = self.email_db.fetch_all_emails()
        self.assertEqual(len(fetched_emails), 2)  # Check the number of emails fetched

        # Check details of each fetched email
        for i, email in enumerate(test_emails):
            fetched_email = fetched_emails[i]
            self.assertEqual(fetched_email[0], email['id'])
            self.assertEqual(fetched_email[1], email['from'])
            self.assertEqual(fetched_email[2], email['subject'])
            self.assertEqual(fetched_email[3], email['date'])
            self.assertEqual(fetched_email[4], email['body'])
