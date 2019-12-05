
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
		res = self.set_webhook()
		print('Set Webhook: ' + str(res['result']))

	def set_webhook(self):
		webhook_url = os.getenv('URL')
		url = self.base_url + 'setWebhook?url=' + webhook_url
		return requests.get(url).json()

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
			elif 'photo' in msg['message'].keys():
				type = 'photo'
				if 'caption' in msg['message']:
					caption = msg['message']['caption']
				else:
					caption = ''
				file_id = msg['message']['photo'][0]['file_id']
				data = (caption, file_id)
				print("[" + date_str + "] " + username + ":  Send photo, caption: " +  ('\'\'' if data[0] == '' else data[0]) + ', file_id: ' + data[1])
			elif 'document' in msg['message'].keys():
				type = 'document'
				if 'caption' in msg['message']:
					caption = msg['message']['caption']
				else:
					caption = ''
				file_id = msg['message']['document']['file_id']
				data = (caption, file_id)
				print("[" + date_str + "] " + username + ":  Send document, caption: " +  ('\'\'' if data[0] == '' else data[0]) + ', file_id: ' + data[1])
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

		if type == 'unknown':
			data = ''
		upd = {'update_id': update_id, 'type': type, 'date': date, 'user_id': user_id, 'username': username, 'data': data}
		return upd

	def get_address(self, lat, lon):
		url = 'https://nominatim.openstreetmap.org/reverse?lat={}&lon={}&format=json'.format(lat, lon)
		res = requests.get(url)
		jsn = res.json()
		return jsn['display_name']

	def extract_menu(self, text):
		menu_dict = {}
		menus = text.split('\n')[1][1:-1].split(']  [')
		for menu in menus:
			k, v = menu.split(': ')
			menu_dict[k] = v
		return menu_dict

	def build_keyboard(self, menu, text):
		reply_markup = {}
		
		# CREATE KEYBOARD
		if menu in ['MAIN'] or (menu == 'CART' and text.startswith('Your Cart is empty')):
			keyb = [['Product List', 'My Cart'], 
					['My Order', "Today's Promo"]]
		elif menu == 'CHECKOUT':
			keyb = [[{'text':'Send Location', 'request_location':True}]]
		elif menu == 'CHECK OUT INPG':
			keyb = [[{'text':'Kirim Sekarang'}],[{'text':'Kirim Ulang Lokasi', 'request_location':True}],[{'text':'Kembali'}]]
		else:
			keyb = None

		# CREATE INLINE KEYBOARD
		if menu in ['PRODUCT']:
			ikeyb = KEYBOARD['product']
		elif menu in ['CART'] and not text.startswith('Your Cart is empty'):
			ikeyb = KEYBOARD['cart']
		elif menu == 'CHECKOUT_CONFIRMATION':
			ikeyb = KEYBOARD['checkout_confirmation']
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

	def send_promo(self, user_id, promo, caption):
		caption_parsed = urllib.parse.quote_plus(caption)
		url = self.base_url + 'sendPhoto?chat_id={}&photo={}&caption={}&parse_mode=Markdown'.format(user_id, promo, caption_parsed)
		url += '&reply_markup={}'.format(self.build_keyboard('MAIN', caption))
		a = requests.get(url).json()

	def send_product(self, user_id, product, caption):
		caption_parsed = urllib.parse.quote_plus(caption)
		url = self.base_url + 'sendPhoto?chat_id={}&photo={}&caption={}&parse_mode=Markdown'.format(user_id, product[3], caption_parsed)
		keyboard = [[]]
		if len(product) == 7:   # for edit order in cart
			for i in range(7):
				if i == 0:
					keyboard.insert(0, [{'text': 'Remove', 'callback_data':'RemoveCart' + str(product[6])}])
				elif i < 6:
					keyboard[1].append({'text': str(i), 'callback_data':'UpdateCart' + str(product[6]) + 'pcs' + str(i)})
				else:
					keyboard[1].append({'text': 'More', 'callback_data':'UpdateCart' + str(product[6]) + 'pcsMore'})	
		else:   # for add product to cart
			for i in range(1, 7):
				if i < 6:
					keyboard[0].append({'text': str(i), 'callback_data':'AddToCart' + str(product[0]) + 'pcs' + str(i)})
				else:
					keyboard[0].append({'text': 'More', 'callback_data':'AddToCart' + str(product[0]) + 'pcsMore'})
		url += '&reply_markup={}'.format(json.dumps({'inline_keyboard': keyboard}))
		requests.get(url)
	
	def send_message(self, user_id, text, menu):
		text_parsed = urllib.parse.quote_plus(text)
		url = self.base_url + 'sendMessage?chat_id={}&text={}&parse_mode=Markdown&disable_web_page_preview=True'.format(user_id, text_parsed)
		keyboard = self.build_keyboard(menu, text)
		if keyboard:
			url += '&reply_markup={}'.format(keyboard)
		res = requests.get(url).json()

	def answer_callback(self, data):
		url_answer = self.base_url + 'answerCallbackQuery?callback_query_id={}'.format(data['callback_query_id'])
		requests.get(url_answer)

	def edit_message(self, text, data):
		self.answer_callback(data)
		text_parsed = urllib.parse.quote_plus(text)
		url = self.base_url + 'editMessageText?message_id={}&chat_id={}&text={}&parse_mode=Markdown&disable_web_page_preview=True'.format(data['message_id'], data['chat_id'], text_parsed)
		
		if data['data'] in ['PRODUCT', 'Cancel', 'Clear', 'CancelToProduct', 'Prev', 'Next'] or  data['data'].startswith(('Sortby', 'FilterCategory', 'OrderProdId')):
			keyboard = KEYBOARD['product']
		elif data['data'] == 'Sort':
			keyboard = KEYBOARD['sort_product']
		elif data['data'] == 'Search':
			keyboard = None
		elif data['data'] == 'Filter':
			keyboard = []
			for category in data['categories']:
				keyboard.append([{'text':'Category: ' + category[0], 'callback_data':'FilterCategory' + category[0].replace(' ', '_')}])
			keyboard.append([{'text':'Cancel', 'callback_data':'CancelToProduct'}])
		elif data['data'] == 'OrderProduct':
			keyboard = []
			for prod in data['products']:
				keyboard.append([{'text': prod[0] + ' - ' + '{:0,.0f}'.format(prod[1]), 'callback_data':'OrderProdId' + str(prod[2])}])
		elif data['data'] == 'EditCart':
			keyboard = []
			for item in data['cart']:
				keyboard.append([{'text': item[0], 'callback_data':'EditCartId' + str(item[1])}])
		elif data['data'] == 'RemoveCart':
			keyboard = KEYBOARD['cart']
		else:
			keyboard = None

		if keyboard:
			url += '&reply_markup={}'.format(json.dumps({'inline_keyboard': keyboard}))
		res = requests.get(url).json()