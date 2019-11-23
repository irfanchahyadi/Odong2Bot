
"""
Bot API
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

import requests, json, time, urllib, os, dotenv
from datetime import datetime
from src.bot_message import KEYBOARD

dotenv.load_dotenv()

class botAPI():
	def __init__(self):
		token = os.getenv('TOKEN')
		self.base_url = 'https://api.telegram.org/bot{}/'.format(token)
		self.timeout = 60

	def get_me(self, key):
		url = self.base_url + 'getMe'
		res = requests.get(url)
		jsn = res.json()
		d = {'id': jsn['result']['id'], 'username': jsn['result']['username']}
		return d[key]

	def get_updates(self, offset):
		url = self.base_url + 'getUpdates?timeout=' + str(self.timeout)
		if offset:
			url += '&offset={}'.format(offset)
		res = requests.get(url)
		jsn = res.json()
		return jsn

	def extract_updates(self, msg):
		update_id = msg['update_id']
		if 'message' in msg.keys():
			user_id = msg['message']['from']['id']
			username = msg['message']['from']['username']
			date = msg['message']['date']
			date = datetime.fromtimestamp(date)
			date_str=date.strftime('%d-%m-%Y %H:%M:%S')
			if 'text' in msg['message'].keys():
				type = 'text'
				data = msg['message']['text']
				print("[" + date_str + "] " + username + ":  " + data)
			elif 'location' in msg['message'].keys():
				type = 'location'
				latitude  = msg['message']['location']['latitude']
				longitude = msg['message']['location']['longitude']
				data = (latitude, longitude)
				print("[" + date_str + "] " + username + ":  Send location, latitude: " +  str(data[0]) + ', longitude: ' + str(data[1]))
			elif 'caption' in msg['message'].keys():
				if 'photo' in msg['message']['caption'].keys():
					type = 'photo'
					caption = msg['message']['caption']
					file_id = msg['message']['photo'][0]['file_id']
					data = (caption, file_id)
					print("[" + date_str + "] " + username + ":  Send photo, caption: " +  ('\'\'' if data[0] == '' else data[0]) + ', file_id: ' + data[1])
				elif 'document' in msg['message']['caption'].keys():
					type = 'document'
					caption = msg['message']['caption']
					file_id = msg['message']['document']['file_id']
					data = (caption, file_id)
					print("[" + date_str + "] " + username + ":  Send document, caption: " +  ('\'\'' if data[0] == '' else data[0]) + ', file_id: ' + data[1])
				else:
					type = 'unknown'
			else:
				type = 'unknown'
		elif 'callback_query' in msg.keys():
			type = 'callback_query'
			user_id = msg['callback_query']['from']['id']
			username = msg['callback_query']['from']['username']
			if 'text' in msg['callback_query']['message'].keys():
				text = msg['callback_query']['message']['text']
			elif 'caption' in msg['callback_query']['message'].keys():
				text = msg['callback_query']['message']['caption']
			data = {'data': msg['callback_query']['data'], 
					'text': text,
					'callback_query_id': msg['callback_query']['id'],
					'message_id': msg['callback_query']['message']['message_id'],
					'chat_id': msg['callback_query']['message']['chat']['id']}
			# date = msg['callback_query']['message']['date']
			date = datetime.now()
			date_str=date.strftime('%d-%m-%Y %H:%M:%S')
			print("[" + date_str + "] " + username + ":  Send callback_query, data: " +  str(data['data']))
		else:
			type = 'unknown'
		upd = {'update_id': update_id, 'type': type, 'date': date, 'user_id': user_id, 'username': username, 'data': data}
		return upd

	def extract_message(self, res, menu):
		type = 'response_message'
		user_id = res['result']['from']['id']
		username = res['result']['from']['username']
		data = {'text': res['result']['text'],
				'data': menu,
				'message_id': res['result']['message_id'],
				'chat_id': res['result']['chat']['id']}
		date = res['result']['date']
		upd = {'type': type, 'date': date, 'user_id': user_id, 'username': username, 'data': data}
		return upd

	def extract_menu(self, text):
		menu_dict = {}
		menus = text.split('\n')[1][1:-1].split(']  [')
		for menu in menus:
			k, v = menu.split(': ')
			menu_dict[k] = v
		return menu_dict

	def build_keyboard(self, menu):
		reply_markup = {}
		
		# CREATE KEYBOARD
		if menu in ['MAIN']:
			keyb = [['Product List', 'My Cart'], 
					['My Order', "Today's Promo"]]
		elif menu == 'CHECK OUT OPEN':
			keyb = [[{'text':'Kirim Lokasi', 'request_location':True}],[{'text':'Kembali'}]]
		elif menu == 'CHECK OUT INPG':
			keyb = [[{'text':'Kirim Sekarang'}],[{'text':'Kirim Ulang Lokasi', 'request_location':True}],[{'text':'Kembali'}]]
		else:
			keyb = None

		# CREATE INLINE KEYBOARD
		if menu in ['PRODUCT']:
			ikeyb = KEYBOARD['product']
		elif menu in ['CART']:
			ikeyb = [[{'text':'Edit', 'callback_data':'EditCart'}, {'text':'Check Out', 'callback_data':'CheckOut'}]]
		else:
			ikeyb = None
		
		if menu in ['HIDE']:
			reply_markup['hide_keyboard']  = True
		elif keyb:
			reply_markup['keyboard'] = keyb
			reply_markup['one_time_keyboard'] = True
			reply_markup['resize_keyboard'] = True
		elif ikeyb:
			reply_markup['inline_keyboard'] = ikeyb
		return json.dumps(reply_markup)

	def delete_message(self, data):
		url = self.base_url + 'deleteMessage?message_id={}&chat_id={}'.format(data['message_id'], data['chat_id'])
		res = requests.get(url)

	def send_photo(self, user_id, product):
		caption = '*' + product[1] + '*\nPrice: ' + '{:0,.0f}'.format(product[2]) + ' \nDescription: ' + product[4] + '\n\nHow many?'
		url = self.base_url + 'sendPhoto?chat_id={}&photo={}&caption={}&parse_mode=Markdown'.format(user_id, product[3], caption)
		keyboard = [[]]
		for i in range(1, 7):
			if i < 6:
				keyboard[0].append({'text': str(i), 'callback_data':'PutToCart' + str(product[0]) + 'pcs' + str(i)})
			else:
				keyboard[0].append({'text': 'More', 'callback_data':'PutToCart' + str(product[0]) + 'pcsMore'})
		url += '&reply_markup={}'.format(json.dumps({'inline_keyboard': keyboard}))
		requests.get(url)
	
	def send_message(self, user_id, text, menu):
		text = urllib.parse.quote_plus(text)
		url = self.base_url + 'sendMessage?chat_id={}&text={}&parse_mode=Markdown&disable_web_page_preview=True'.format(user_id, text)
		keyboard = self.build_keyboard(menu)
		if keyboard:
			url += '&reply_markup={}'.format(keyboard)
		res = requests.get(url).json()
		return self.extract_message(res, menu)

	def edit_message(self, text, data):
		url_answer = self.base_url + 'answerCallbackQuery?callback_query_id={}'.format(data['callback_query_id'])
		url = self.base_url + 'editMessageText?message_id={}&chat_id={}&text={}&parse_mode=Markdown&disable_web_page_preview=True'.format(data['message_id'], data['chat_id'], text)
		
		if data['data'] in ['PRODUCT', 'Cancel', 'Clear', 'Prev', 'Next'] or  data['data'].startswith(('Sortby', 'FilterCategory', 'OrderProdId')):
			keyboard = KEYBOARD['product']
		elif data['data'] == 'Sort':
			keyboard = KEYBOARD['sort_product']
		elif data['data'] == 'Search':
			keyboard = None
		elif data['data'] == 'Filter':
			keyboard = []
			for category in data['categories']:
				keyboard.append([{'text':'Category: ' + category[0], 'callback_data':'FilterCategory' + category[0].replace(' ', '_')}])
			keyboard.append([{'text':'Cancel', 'callback_data':'Cancel'}])
		elif data['data'] == 'OrderProduct':
			keyboard = []
			for prod in data['products']:
				keyboard.append([{'text': prod[0] + ' - ' + '{:0,.0f}'.format(prod[1]), 'callback_data':'OrderProdId' + str(prod[2])}])
		else:
			keyboard = None

		if keyboard:
			url += '&reply_markup={}'.format(json.dumps({'inline_keyboard': keyboard}))
		res = requests.get(url).json()
		requests.get(url_answer)
		# print(res)