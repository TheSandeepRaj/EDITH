# Import the required modules

import os
import time
from io import BytesIO
import speech_recognition as sr
import pyttsx3 
import datetime
import subprocess
import requests

import google_calendar as gc
import config

username = 'Sandeep'

# for Calendar
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june','july', 'august', 'september','october', 'november', 'december']
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] 		# in datetime module	date.weekday()  Monday is 0 and Sunday is 6 
DAY_EXTENTIONS = ['st', 'nd', 'rd', 'th']




def speak(text):
	print(text)
	engine = pyttsx3.init()
	engine.setProperty('rate',150)
	engine.setProperty('volume',2.0)
	engine.say(text)
	engine.runAndWait()


def get_audio():
	rec = sr.Recognizer()
	with sr.Microphone() as source:
		print('Sepak Now')
		audio = rec.listen(source)
		said = ''
		try:
			said = rec.recognize_google(audio)
			print(said)
		except Exception as e:
			print ('Exception: ' + str(e))
	return said.lower()


def get_date(text):             # Function to grab a date from input (speech)
	today = datetime.date.today()

	if text.count('today') > 0:     # if user mentioned today > 0 in input
		return today

	day = -1
	day_of_week = -2
	month = -1
	year = today.year

	for word in text.split():
		if word in MONTHS:
			month = MONTHS.index(word) + 1 		#in
		elif word in DAYS:
			day_of_week = DAYS.index(word)
		elif word.isdigit():
			day = int(word)
		else:
			for ext in DAY_EXTENTIONS:
				found = word.find(ext)
				if found > 0:
					try:
						day = int(word[:found])
					except:
						pass

	if (month < today.month) and (month != -1):
		year += 1

	if (day < today.day) and (month == -1) and (day != -1):
		month += 1

	if (month == -1) and (day == -1) and (day_of_week != -1):
		current_day_of_week = today.weekday()
		diff = day_of_week - current_day_of_week
		if (diff < 0) :
			diff += 7
			if text.count('next') >= 1:
				diff += 7
		return today + datetime.timedelta(diff)
	if (month == -1) or (day == -1):
		return None
	
	return datetime.date(month=month, day=day, year=year)


def note(text):
	date = datetime.datetime.now()
	file_name = str(date).replace(':', '-') + '-note.txt'
	with open(file_name, 'w') as f:
		f.write(text)

	subprocess.Popen(['notepad.exe', file_name])


def appliances(pin, value):	
	base_url = "http://cloud.blynk.cc/" 
	url = base_url + config.Auth_token + '/update/' + pin + '?value=' + value
	requests.get(url, verify=False)


if __name__ == '__main__':

	speak("Hello {}! I'm EDITH, your personal assistant.".format(username))
	print('''You can ask me things like :
	- what is your upcomming event on calender
	- control the appliances e.g. Light and Fan
	''')

	text = get_audio()


	# intro
	intro_str = ['who are you', 'what is your name', ]
	for phrase in intro_str:
		if phrase in text:
			speak('My name is EDITH')


	# for calendar
	SERVICE = gc.auth_google()
	calendar_str = ['what do i have', 'do i have plans', 'am i busy', 'what am i doing']
	for phrase in calendar_str:
		if phrase in text:
			date = get_date(text)
			if date:
				gc.get_events(date, SERVICE)
			else:
				speak('Please Try Again')


	# for note
	note_str = ['make a note', 'write this down', 'remember this', 'type this', 'save this']
	for phrase in note_str:
		if phrase in text:
			speak('What would you like me to write down? ')
			write_down = get_audio()
			note(write_down)
			speak("I've made a note of that.")	

	# for control appliances

	light_on = ['turn on light', 'turn on the light', 'light on', "it's dark here", "it is dark here", "i'm home", 'i am home']
	for phrase in light_on:
		if phrase in text:
			speak('Okay, Turning on the light.')
			appliances('D4', '1')

	light_off = ['turn off light', 'turn  the light', 'light off', 'good night', 'good night!']
	for phrase in light_off:
		if phrase in text:
			speak('Okay, Turning off the light.')
			appliances('D4', '0')

	fan_on = ['turn on fan', 'fan on', 'turn on the fan', 'fan on', "it's hot here", "it is hot here", "it is hot"] 			# TODO: turn on fan acc tempr
	for phrase in fan_on:
		if phrase in text:
			speak('Okay, Turning on the fan.')
			appliances('D5', '1')

	fan_off = ['turn off fan', 'fan off', 'turn off the fan']
	for phrase in fan_off:
		if phrase in text:
			speak('Okay, Turning off the fan.')
			appliances('D5', '0')

