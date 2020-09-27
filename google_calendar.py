from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pytz

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def auth_google():
	"""Shows basic usage of the Google Calendar API.
	Prints the start and name of the next n events on the user's calendar.
	"""
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
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('calendar', 'v3', credentials=creds)

	return service

def get_events(day, service):					#day is date  YYYY-MM-DD[*HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]]

	# Call the Calendar API
	date = datetime.datetime.combine(day, datetime.datetime.min.time())
	end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
	utc = pytz.UTC
	date = date.astimezone(utc)
	end_date = end_date.astimezone(utc)


	events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), 
										timeMax=end_date.isoformat(), singleEvents=True,
										orderBy='startTime').execute()
	events = events_result.get('items', [])

	if not events:
		speak('No upcoming events found.')
	else:
		speak(f'You have {len(events)} events on this day.')

	for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])  # get the hour from event
            if int(start_time.split(":")[0]) < 12:			# for am time
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]		# for am time
                start_time = start_time + "pm"  

            speak(event["summary"] + " at " + start_time)

# if __name__ == '__main__':
#     service = auth_google()
#     get_events(2, service)