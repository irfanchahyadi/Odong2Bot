
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
			date = msg['message']['date']
			user_id = msg['message']['from']['id']
			username = msg['message']['from']['username']
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
					caption = msg['message']['caption']
					file_id = msg['message']['photo'][0]['file_id']
					data = (caption, file_id)
				elif 'document' in msg['message']['caption'].keys():
					type = 'document'
					caption = msg['message']['caption']
					file_id = msg['message']['document']['file_id']
					data = (caption, file_id)
				else:
					type = 'unknown'
			else:
				type = 'unknown'
		elif 'callback_query' in msg.keys():
			type = 'callback_query'
			date = msg['callback_query']['message']['date']
			user_id = msg['callback_query']['from']['id']
			username = msg['callback_query']['from']['username']
			data = msg['callback_query']['data']
		else:
			type = 'unknown'
		return update_id, type, date, user_id, username, data

	def build_keyboard(menu, hide=False):
		if not hide:
			if menu == 'MAIN':
				keyb = [['Order Gan!', 'List Produk'], 
						['Keranjang', 'Pesanan Anda']]
			elif menu == 'LIST PRODUK':
				keyb = [['Semua Produk', 'Kategori Produk'], 
						['Pencarian Produk', 'Kembali']]
			elif menu == 'CHECK OUT OPEN':
				keyb = [[{'text':'Kirim Lokasi', 'request_location':True}],[{'text':'Kembali'}]]
			elif menu == 'CHECK OUT INPG':
				keyb = [[{'text':'Kirim Sekarang'}],[{'text':'Kirim Ulang Lokasi', 'request_location':True}],[{'text':'Kembali'}]]
		if hide:
			reply_markup = {'hide_keyboard': True}
		else:
			reply_markup = {'keyboard':keyb, 'one_time_keyboard':True, 'resize_keyboard':True}
		return json.dumps(reply_markup)

	def send_message(self, user_id, text, reply_markup=None):
		text = urllib.parse.quote_plus(text)
		url = self.base_url + 'sendMessage?chat_id={}&text={}&parse_mode=Markdown&disable_web_page_preview=True'.format(user_id, text)
		if reply_markup:
			url += '&reply_markup={}'.format(reply_markup)
		requests.get(url) 