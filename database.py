import sqlite3


class EmailDatabase:
    def __init__(self, db_file='database.db'):
        self.conn = sqlite3.connect(db_file)
        self._create_table()

    def _create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT,
                subject TEXT,
                date TEXT,
                body TEXT
            )
        ''')

    def store_emails(self, emails):
        # Use executemany for bulk insert
        self.conn.executemany('''
            INSERT INTO emails (id, sender, subject, date, body)
            VALUES (?, ?, ?, ?, ?)
        ''', [(email['id'], email['from'], email['subject'], email['date'], email['body']) for email in emails])
        self.conn.commit()

    def fetch_all_emails(self):
        return self.conn.execute("SELECT * FROM emails").fetchall()
