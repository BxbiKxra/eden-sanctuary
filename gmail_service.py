"""
Gmail Service Module
Provides Gmail API integration with OAuth2 authentication
Supports email reading, sending, and management
"""
import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]


class GmailService:
    """Gmail API service wrapper"""

    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        """
        Initialize Gmail service

        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store OAuth2 token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.creds = None

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load existing token if available
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)

            # Refresh or get new credentials
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        print(f"Error: {self.credentials_file} not found")
                        print("Please download OAuth2 credentials from Google Cloud Console")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    self.creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)

            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            return True

        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def get_messages(self, query: str = '', max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get messages from Gmail inbox

        Args:
            query: Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')
            max_results: Maximum number of messages to retrieve

        Returns:
            List of message dictionaries
        """
        if not self.service:
            if not self.authenticate():
                return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            detailed_messages = []

            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                detailed_messages.append(self._parse_message(msg_data))

            return detailed_messages

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def _parse_message(self, msg_data: Dict) -> Dict[str, Any]:
        """Parse Gmail message data into a readable format"""
        headers = msg_data['payload']['headers']

        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        to = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')

        # Get message body
        body = ''
        if 'parts' in msg_data['payload']:
            for part in msg_data['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        elif 'body' in msg_data['payload'] and 'data' in msg_data['payload']['body']:
            body = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode('utf-8')

        return {
            'id': msg_data['id'],
            'threadId': msg_data['threadId'],
            'subject': subject,
            'from': sender,
            'to': to,
            'date': date,
            'body': body,
            'snippet': msg_data.get('snippet', ''),
            'labels': msg_data.get('labelIds', [])
        }

    def send_email(self, to: str, subject: str, body: str,
                   from_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an email via Gmail

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (defaults to authenticated user)

        Returns:
            Dictionary with send status
        """
        if not self.service:
            if not self.authenticate():
                return {'success': False, 'error': 'Authentication failed'}

        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            if from_email:
                message['from'] = from_email

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return {
                'success': True,
                'message_id': send_result['id'],
                'thread_id': send_result['threadId']
            }

        except HttpError as error:
            return {'success': False, 'error': str(error)}

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        if not self.service:
            if not self.authenticate():
                return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error marking message as read: {error}')
            return False

    def archive_message(self, message_id: str) -> bool:
        """Archive a message (remove from inbox)"""
        if not self.service:
            if not self.authenticate():
                return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error archiving message: {error}')
            return False

    def delete_message(self, message_id: str) -> bool:
        """Delete a message permanently"""
        if not self.service:
            if not self.authenticate():
                return False

        try:
            self.service.users().messages().delete(
                userId='me',
                id=message_id
            ).execute()
            return True
        except HttpError as error:
            print(f'Error deleting message: {error}')
            return False

    def get_labels(self) -> List[Dict[str, str]]:
        """Get all Gmail labels"""
        if not self.service:
            if not self.authenticate():
                return []

        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            return [{'id': label['id'], 'name': label['name']} for label in labels]
        except HttpError as error:
            print(f'Error fetching labels: {error}')
            return []

    def search_messages(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search messages with advanced Gmail query

        Examples:
            - 'is:unread' - Unread messages
            - 'from:example@gmail.com' - From specific sender
            - 'subject:important' - Subject contains 'important'
            - 'has:attachment' - Messages with attachments
            - 'after:2024/01/01' - Messages after date
        """
        return self.get_messages(query=query, max_results=max_results)

    def get_user_profile(self) -> Dict[str, str]:
        """Get authenticated user's Gmail profile"""
        if not self.service:
            if not self.authenticate():
                return {}

        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                'email': profile.get('emailAddress', ''),
                'messages_total': profile.get('messagesTotal', 0),
                'threads_total': profile.get('threadsTotal', 0)
            }
        except HttpError as error:
            print(f'Error fetching profile: {error}')
            return {}


# Singleton instance for easy access
_gmail_service_instance = None

def get_gmail_service() -> GmailService:
    """Get or create Gmail service singleton"""
    global _gmail_service_instance
    if _gmail_service_instance is None:
        _gmail_service_instance = GmailService()
    return _gmail_service_instance
