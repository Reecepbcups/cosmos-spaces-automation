from __future__ import print_function

import os.path
from os import getenv

from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# load dot.env
from dotenv import load_dotenv
load_dotenv()

'''
NOTES; use datetime.utcnow() for any times so we don't have to deal with timezone stuff
'''

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CalendarID = getenv('CALENDAR_ID', "primary")

def load_credentials() -> Credentials:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def print_upcoming_events(events):
    if not events:
        print('No upcoming events found.')
        return    
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = load_credentials()

    try:
        service = build('calendar', 'v3', credentials=creds)
          
        now = datetime.utcnow().isoformat() + 'Z' # 2022-10-03T20:34:18.562795Z       

        events = get_events_on_a_day(service, max_results=50, iso_format_date=now)

        print_upcoming_events(events)

    except HttpError as error:
        print('An error occurred: %s' % error)


def get_events_on_a_day(service, max_results=10, iso_format_date=datetime.utcnow().isoformat() + 'Z') -> list:    
    events_result = service.events().list(
        calendarId=CalendarID, timeMin=iso_format_date,
        maxResults=max_results, singleEvents=True,
        orderBy='startTime'
    ).execute()    
    return events_result.get('items', [])


def add_event_to_calendar(title: str = "", description: str = "", spaces_url: str = "", start_time_iso_format: str | datetime = ""):    
    creds = load_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    # convert to string format of ISO 8601 + Z
    if isinstance(start_time_iso_format, datetime):
        start_time_iso_format = start_time_iso_format.isoformat() + 'Z'
    elif isinstance(start_time_iso_format, str):
        if start_time_iso_format == "":
            start_time_iso_format = datetime.utcnow().isoformat() + 'Z'


    start_time = datetime.fromisoformat(start_time_iso_format[:-1]) # removes the Z at the end   
    end_time = start_time + timedelta(hours=1) # we always set as +1 to show any overlap.    
    
    events_on_this_day = get_events_on_a_day(service, max_results=50, iso_format_date=start_time.isoformat() + 'Z')    
    
    # do the above in 1 line
    if any(event['summary'] == title for event in events_on_this_day):
        print("Event already exists, not adding")
        return

    # exit()
    print(f"Adding event-> '{title}'")

    event = {
        'summary': title,
        'description': description,
        'location': '',
        'source': {
            "url": spaces_url,
        },
        'start': {
            'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                #  {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},                
            ],
        },
    }

    event = service.events().insert(calendarId=CalendarID, body=event).execute()


if __name__ == '__main__':
    # main()
    add_event_to_calendar(
        title="My Spaces Title1", 
        description="Run by XYZ about...", 
        spaces_url="https://twitter.com",
        start_time_iso_format=datetime.utcnow()+timedelta(minutes=30),        
    )
