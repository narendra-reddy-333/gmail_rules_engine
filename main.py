# main.py
from gmail_api import GmailAPI
from database import EmailDatabase
from rules import RulesProcessor


def main():
    # Initialize Gmail API client
    gmail_api = GmailAPI()
    # fetch emails
    emails = gmail_api.fetch_emails()

    # Initialize Email Database
    email_db = EmailDatabase()
    # create email table
    email_db.create_table()
    # Store emails in database

    email_db.store_emails(emails)

    # Initialize Rules Parser.
    rules_parser = RulesProcessor(gmail_api=gmail_api, email_db=email_db)
    # Process emails based on rules
    processed_emails = rules_parser.process_emails()


if __name__ == '__main__':
    main()
