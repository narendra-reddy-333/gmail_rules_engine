import sqlite3


class EmailDatabase:
    def __init__(self, db_file='database.db'):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT,
                subject TEXT,
                date TEXT,
                body TEXT
            )
        ''')
        self.conn.commit()

    def store_emails(self, emails):
        cursor = self.conn.cursor()
        for email in emails:
            cursor.execute('''
                INSERT INTO emails (id, sender, subject, date, body)
                VALUES (?, ?, ?, ?, ?)
            ''', (email['id'], email['from'], email['subject'], email['date'], email['body']))
        self.conn.commit()

    def fetch_all_emails(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM emails")
        return cursor.fetchall()
