import base64
import os.path
import pickle
from email import parser

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']


class GmailAPI:
    def __init__(self):
        self.service = self._get_gmail_service()

    @staticmethod
    def _get_gmail_service():
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('gmail', 'v1', credentials=creds)
        return service

    def fetch_emails(self, query=None, max_results=10):
        results = self.service.users().messages().list(userId='me', q=query,
                                                       maxResults=max_results).execute()
        messages = results.get('messages', [])
        email_data = []
        for message in messages:
            msg = self.service.users().messages().get(userId='me', id=message['id'],
                                                      format='raw').execute()
            msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
            mime_msg = parser.Parser().parsestr(msg_str.decode())
            email_data.append({
                'id': message['id'],
                'from': mime_msg['From'],
                'subject': mime_msg['Subject'],
                'date': mime_msg['Date'],
                'body': self._get_body(mime_msg)
            })
        return email_data

    @staticmethod
    def _get_body(msg):
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                # skip any attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    return part.get_payload(decode=True).decode()  # decode
        else:
            return msg.get_payload(decode=True).decode()

    def mark_as_read(self, message_id):
        self.service.users().messages().modify(userId='me', id=message_id,
                                               body={'removeLabelIds': ['UNREAD']}).execute()

    def mark_as_unread(self, message_id):
        self.service.users().messages().modify(userId='me', id=message_id,
                                               body={'addLabelIds': ['UNREAD']}).execute()

    def move_to_label(self, message_id, label_id):
        self.service.users().messages().modify(userId='me', id=message_id,
                                               body={'addLabelIds': [label_id],
                                                     'removeLabelIds': ['INBOX']}).execute()

    def get_label_id(self, label_name):
        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        for label in labels:
            if label['name'] == label_name:
                return label['id']
        return None  # Label not found

    def move_to_folder(self, message_id, folder_name):
        if folder_name in ['Trash', 'Spam']:
            self.service.users().messages().trash(userId='me', id=message_id).execute()
        elif folder_name == 'Inbox':
            self.service.users().messages().untrash(userId='me', id=message_id).execute()
        else:
            raise ValueError("Invalid folder name")
