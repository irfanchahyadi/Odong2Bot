
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
			text = db.get_products()
			api.send_message(upd['user_id'], text, 'PRODUCT')
		elif upd['data'] == 'My Cart':
			text = db.get_cart(upd['user_id'])
			api.send_message(upd['user_id'], text, 'CART')
		elif upd['data'] == 'My Order':
			text = db.get_order(upd['user_id'])
			api.send_message(upd['user_id'], text, 'MAIN')
		elif upd['data'] == "Today's Promo":
			promos = db.get_promo()
			for promo in promos:
				api.send_promo(upd['user_id'], promo[0], promo[1])
		elif db.get_user_last_menu(upd['user_id'])['State'] == 'Search':
			db.set_user_last_menu(upd['user_id'], {'State': '', 'Search': upd['data']})
			menu = db.get_user_last_menu(upd['user_id'])
			text = db.get_products(menu)
			api.send_message(upd['user_id'], text, 'PRODUCT')
		elif db.get_user_last_menu(upd['user_id'])['State'].startswith('AddToCart'):
			prod_id = db.get_user_last_menu(upd['user_id'])['State'][9:-7]
			db.set_user_last_menu(upd['user_id'], {'State': ''})
			if upd['data'].isdigit():
				db.add_cart(upd['user_id'], prod_id, int(upd['data']))
				api.send_message(upd['user_id'], MESSAGE['added_cart'], 'MAIN')
		elif db.get_user_last_menu(upd['user_id'])['State'].startswith('UpdateCart'):
			item_id = db.get_user_last_menu(upd['user_id'])['State'][10:-7]
			db.set_user_last_menu(upd['user_id'], {'State': ''})
			if upd['data'].isdigit():
				db.update_cart(item_id, upd['data'])
				text = db.get_cart(upd['user_id'])
				api.send_message(upd['user_id'], text, 'CART')
		elif db.get_user_last_menu(upd['user_id'])['State'] == 'CheckoutConfirmation':
			db.set_user_last_menu(upd['user_id'], {'Note': upd['data'], 'State': ''})
			last_menu = db.get_user_last_menu(upd['user_id'])
			text = '*CHECKOUT CONFIRMATION*'
			text += '\n\n' + db.get_cart(upd['user_id']).replace('Your Cart:', 'Your Order:')
			text += '\n\n*Delivery Address:*\n' + last_menu['Address']
			text += '\n\n*Note:*\n' + upd['data']
			text += '\n\n*Process?*'
			api.send_message(upd['user_id'], text, 'CHECKOUT_CONFIRMATION')
	elif upd['type'] == 'location':
		lat, lon = upd['data']
		address = api.get_address(lat, lon)
		db.set_user_last_menu(upd['user_id'], {'State': 'CheckoutConfirmation', 'Address': address, 'Lat': lat, 'Lon': lon})
		text = 'Delivery address:\n' + address + '\n\nAdd note:'
		api.send_message(upd['user_id'], text, 'NONE')
	elif upd['type'] == 'callback_query':
		data = upd['data']
		if data['data'].startswith(('Sort', 'Search', 'Filter', 'Order', 'Clear', 'Next', 'Prev')):
			if data['text'].split('\n')[0] == 'List Product':
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
			elif data['data'] == 'OrderProduct':
				text = 'Pick to buy:'
				db.set_user_last_menu(upd['user_id'], {'State': 'Order'})
				data['products'] = db.get_products(menu, with_id=True)
			else:
				if data['data'].startswith('Sortby'):
					db.set_user_last_menu(upd['user_id'], {'Sort': data['data'][6:]})
				elif data['data'].startswith('FilterCategory'):
					db.set_user_last_menu(upd['user_id'], {'Filter': data['data'][14:].replace('_', ' ')})
				elif data['data'] == 'Clear':
					db.set_user_last_menu(upd['user_id'], 'clear')
				elif data['data'].startswith('OrderProdId'):
					product = db.get_product_detail(data['data'][11:])
					caption = '*' + product[1] + '*\n\n*Price:* ' + '{:0,.0f}'.format(product[2]) + ' \n*Description:* ' + product[4] + '\n\nHow many?'
					api.send_product(upd['user_id'], product, caption)
				elif data['data'].startswith('OrderProdOkId'):
					prod_id, pcs = data['data'][13:].split('pcs')
				elif data['data'] in ['Prev', 'Next']:
					last_page = int(db.get_user_last_menu(upd['user_id'])['Page'])
					if data['data'] == 'Prev' and last_page > 1:
						db.set_user_last_menu(upd['user_id'], {'Page': last_page - 1})
					elif data['data'] == 'Next':
						db.set_user_last_menu(upd['user_id'], {'Page': last_page + 1})
				menu = db.get_user_last_menu(upd['user_id'])
				text = db.get_products(menu)
			api.edit_message(text, data)
		elif data['data'].startswith('AddToCart') and data['data'].endswith('More'):
			db.set_user_last_menu(upd['user_id'], {'State': data['data']})
			prod = data['text'].split('\n')[0]
			text = 'How many *' + prod + '* do you want?'
			api.delete_message(data)
			api.send_message(upd['user_id'], text, 'NONE')
		elif data['data'].startswith('AddToCart'):
			prod_id, quantity = data['data'][9:].split('pcs')
			db.add_cart(upd['user_id'], prod_id, quantity)
			api.delete_message(data)
			api.send_message(upd['user_id'], MESSAGE['added_cart'], 'MAIN')
		elif data['data'].startswith('EditCartId'):
			item = db.get_cart_detail(data['data'][10:])
			caption = '*' + item[1] + '*\n\n*Price:* ' + '{:0,.0f}'.format(item[2]) + ' \n*Description:* ' + item[4] + '\n*Quantity:* ' + str(item[5])
			api.delete_message(data)
			api.send_product(upd['user_id'], item, caption)
		elif data['data'] == 'EditCart':
			text = 'Edit item on cart:'
			data['cart'] = db.get_cart(upd['user_id'], type='option')
			api.edit_message(text, data)
		elif data['data'].startswith('RemoveCart'):
			db.remove_cart(data['data'][10:])
			text = db.get_cart(upd['user_id'])
			api.delete_message(data)
			api.send_message(upd['user_id'], text, 'CART')
		elif data['data'].startswith('UpdateCart') and data['data'].endswith('More'):
			db.set_user_last_menu(upd['user_id'], {'State': data['data']})
			prod = data['text'].split('\n')[0]
			text = 'How many *' + prod + '* do you want?'
			api.delete_message(data)
			api.send_message(upd['user_id'], text, 'NONE')
		elif data['data'].startswith('UpdateCart'):
			item_id, quantity = data['data'][10:].split('pcs')
			db.update_cart(item_id, quantity)
			text = db.get_cart(upd['user_id'])
			api.delete_message(data)
			api.send_message(upd['user_id'], text, 'CART')
		elif data['data'] == 'Checkout':
			api.answer_callback(data)
			api.send_message(upd['user_id'], MESSAGE['ask_location'], 'CHECKOUT')
		elif data['data'] == 'CancelCheckout':
			text = db.get_cart(upd['user_id'])
			api.delete_message(data)
			api.send_message(upd['user_id'], text, 'CART')
		elif data['data'] == 'ProcessCheckout':
			api.answer_callback(data)
			db.add_order(upd['user_id'])
			api.send_message(upd['user_id'], MESSAGE['added_order'], 'MAIN')


if __name__ == '__main__':
	db = dbHelper(init_setup=True)
	api = botAPI()
	last_update_id = 0
	print('Listening to: ' + api.get_me('username'))
	while True:
		jsn = api.get_updates(last_update_id)
		if jsn['ok']:
			for msg in jsn['result']:
				upd = api.extract_updates(msg)
				last_update_id = max(last_update_id, upd['update_id']) + 1
				handler(upd)
		time.sleep(1)