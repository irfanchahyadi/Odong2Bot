
"""
Bot API
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

import requests, json, time, urllib

class botAPI():
	def __init__(self):
		token = '349250675:AAG7b0SqINmphIvAYHL7riaJcZgNAd-OMTY'
		self.base_url = 'https://api.telegram.org/bot{}/'.format(token)
		self.timeout = 60

	def get_updates(self):
		url = self.base_url + 'getUpdates?timeout=' + str(self.timeout)
		res = requests.get(url)
		jsn = res.json()
		if jsn['ok']:
			for msg in jsn['result']:
				type, date, user, data = self.extract_updates(msg)
				print(type, date, user, data)
		
	def extract_updates(self, msg):
		if 'message' in msg.keys():
			date = msg['message']['date']
			user = msg['message']['from']['id']
			if 'text' in msg['message'].keys():
				type = 'text'
				data = msg['message']['text']
			elif 'location' in msg['message'].keys():
				type = 'location'
				latitude  = msg['message']['location']['latitude']
				longitude = msg['message']['location']['longitude']
				data = (latitude, longitude)
			elif 'caption' in msg['message'].keys():
				if 'photo' in msg['message']['caption'].keys():
					type = 'photo'
				elif 'document' in msg['message']['caption'].keys():
					type = 'document'
				else:
					type = 'unknown'
			else:
				type = 'unknown'
		elif 'callback_query' in msg.keys():
			type = 'callback_query'
		else:
			type = 'unknown'
		return type, date, user, data