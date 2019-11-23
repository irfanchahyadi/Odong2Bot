
"""
Main File
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

from src.db_helper import dbHelper
from src.bot_api import botAPI
from src.bot_message import MESSAGE
import time, json

def handler(upd):
	if upd['type'] == 'text':
		if upd['data'] == '/start':
			db.add_user(upd['user_id'], upd['username'])
			api.send_message(upd['user_id'], MESSAGE['welcome'], 'MAIN')
		elif upd['data'] == 'Product List':
			db.set_user_last_menu(upd['user_id'], 'clear')
			text = db.get_product()
			# api.send_message(upd['user_id'], MESSAGE['list_product'], 'HIDE')
			api.send_message(upd['user_id'], text, 'PRODUCT')
		elif db.get_user_last_menu(upd['user_id'])['State'] == 'Search':
			db.set_user_last_menu(upd['user_id'], {'State': '', 'Search': upd['data']})
			menu = db.get_user_last_menu(upd['user_id'])
			print(menu)
			text = db.get_product(menu)
			api.send_message(upd['user_id'], text, 'PRODUCT')

	elif upd['type'] == 'callback_query':
		data = upd['data']
		if data['text'][0] == '[':
			menu = api.extract_menu(data['text'])
			db.set_user_last_menu(upd['user_id'], menu)
		if data['data'] == 'Sort':
			text = 'Sort by :'
		elif data['data'] == 'Search':
			db.set_user_last_menu(upd['user_id'], {'State': 'Search'})
			text = 'Type keyword for search :'
		elif data['data'] == 'Filter':
			text = 'Filter by category :'
			categories = db.get_product_category()
			data['categories'] = categories
		elif data['data'][:8] == 'Filterby':
			text = data['text']
		else:
			if data['data'].startswith('Sortby'):
				db.set_user_last_menu(upd['user_id'], {'Sort': data['data'][6:]})
			elif data['data'].startswith('FCategory'):
				db.set_user_last_menu(upd['user_id'], {'Filter': data['data'][9:].replace('_', ' ')})
			menu = db.get_user_last_menu(upd['user_id'])
			text = db.get_product(menu)
			# print(text)
		api.edit_message(text, data)
		pass

if __name__ == '__main__':
	db = dbHelper(init_setup=True)
	api = botAPI()
	last_update_id = 0
	while True:
		jsn = api.get_updates(last_update_id)
		if jsn['ok']:
			for msg in jsn['result']:
				upd = api.extract_updates(msg)
				last_update_id = max(last_update_id, upd['update_id']) + 1
				handler(upd)
		time.sleep(1)