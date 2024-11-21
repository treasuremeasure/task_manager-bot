from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle

class GoogleCalendarService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar',
                       'https://www.googleapis.com/auth/calendar.events']
        self.creds = None
        self.service = None
        self.initialize_credentials()

    def initialize_credentials(self):
        # Проверяем существование token.pickle
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # Если нет валидных credentials, создаем новые
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Сохраняем credentials для следующего запуска
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def add_event(self, task_name, description, deadline):
        event = {
            'summary': task_name,
            'description': description,
            'start': {
                'date': deadline.strftime('%Y-%m-%d'),
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'date': deadline.strftime('%Y-%m-%d'),
                'timeZone': 'Europe/Moscow',
            },
            'reminders': {
                'useDefault': True
            }
        }

        try:
            event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            return event.get('htmlLink')
        except Exception as e:
            print(f'Ошибка при создании события: {e}')
            return None