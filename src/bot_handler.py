
"""
Bot Handler
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

from src.db_helper import dbHelper
from src.bot_api import botAPI
from src.bot_message import MESSAGE

class Handler():
	def __init__(self):
		self.db = dbHelper(init_setup=False)
		self.api = botAPI()

	def set_webhook(self):
		res = self.api.set_webhook()
		return res

	def reset_db(self):
		self.db.reset_db()

	def get_me(self):
		return self.api.get_me('username')

	def get_updates(self, last_update_id):
		return self.api.get_updates(last_update_id)

	def extract_updates(self, msg):
		return self.api.extract_updates(msg)

	def handle(self, upd):
		if upd['type'] == 'text':
			if upd['data'] == '/start':
				self.db.add_user(upd['user_id'], upd['username'])
				self.api.send_message(upd['user_id'], MESSAGE['welcome'], 'MAIN')
			elif upd['data'] == 'Product List':
				self.db.set_user_last_menu(upd['user_id'], 'clear')
				text = self.db.get_products()
				self.api.send_message(upd['user_id'], text, 'PRODUCT')
			elif upd['data'] == 'My Cart':
				text = self.db.get_cart(upd['user_id'])
				self.api.send_message(upd['user_id'], text, 'CART')
			elif upd['data'] == 'My Order':
				text = self.db.get_order(upd['user_id'])
				self.api.send_message(upd['user_id'], text, 'MAIN')
			elif upd['data'] == "Today's Promo":
				promos = self.db.get_promo()
				for promo in promos:
					self.api.send_promo(upd['user_id'], promo[0], promo[1])
			elif self.db.get_user_last_menu(upd['user_id'])['State'] == 'Search':
				self.db.set_user_last_menu(upd['user_id'], {'State': '', 'Search': upd['data']})
				menu = self.db.get_user_last_menu(upd['user_id'])
				text = self.db.get_products(menu)
				self.api.send_message(upd['user_id'], text, 'PRODUCT')
			elif self.db.get_user_last_menu(upd['user_id'])['State'].startswith('AddToCart'):
				prod_id = self.db.get_user_last_menu(upd['user_id'])['State'][9:-7]
				self.db.set_user_last_menu(upd['user_id'], {'State': ''})
				if upd['data'].isdigit():
					self.db.add_cart(upd['user_id'], prod_id, int(upd['data']))
					self.api.send_message(upd['user_id'], MESSAGE['added_cart'], 'MAIN')
			elif self.db.get_user_last_menu(upd['user_id'])['State'].startswith('UpdateCart'):
				item_id = self.db.get_user_last_menu(upd['user_id'])['State'][10:-7]
				self.db.set_user_last_menu(upd['user_id'], {'State': ''})
				if upd['data'].isdigit():
					self.db.update_cart(item_id, upd['data'])
					text = self.db.get_cart(upd['user_id'])
					self.api.send_message(upd['user_id'], text, 'CART')
			elif self.db.get_user_last_menu(upd['user_id'])['State'] == 'CheckoutConfirmation':
				self.db.set_user_last_menu(upd['user_id'], {'Note': upd['data'], 'State': ''})
				last_menu = self.db.get_user_last_menu(upd['user_id'])
				text = '*CHECKOUT CONFIRMATION*'
				text += '\n\n' + self.db.get_cart(upd['user_id']).replace('Your Cart:', 'Your Order:')
				text += '\n\n*Delivery Address:*\n' + last_menu['Address']
				text += '\n\n*Note:*\n' + upd['data']
				text += '\n\n*Process?*'
				self.api.send_message(upd['user_id'], text, 'CHECKOUT_CONFIRMATION')
		elif upd['type'] == 'location':
			lat, lon = upd['data']
			address = self.api.get_address(lat, lon)
			self.db.set_user_last_menu(upd['user_id'], {'State': 'CheckoutConfirmation', 'Address': address, 'Lat': lat, 'Lon': lon})
			text = 'Delivery address:\n' + address + '\n\nAdd note:'
			self.api.send_message(upd['user_id'], text, 'NONE')
		elif upd['type'] == 'callback_query':
			data = upd['data']
			if data['data'].startswith(('Sort', 'Search', 'Filter', 'Order', 'Clear', 'CancelToProduct', 'Next', 'Prev')):
				if data['text'].split('\n')[0] == 'List Product':
					menu = self.api.extract_menu(data['text'])
					self.db.set_user_last_menu(upd['user_id'], menu)
				if data['data'] == 'Sort':
					text = 'Sort by :'
				elif data['data'] == 'Search':
					self.db.set_user_last_menu(upd['user_id'], {'Page': 1, 'State': 'Search'})
					text = 'Type keyword for search :'
				elif data['data'] == 'Filter':
					text = 'Filter by category :'
					categories = self.db.get_product_category()
					data['categories'] = categories
				elif data['data'] == 'OrderProduct':
					text = 'Pick to buy:'
					self.db.set_user_last_menu(upd['user_id'], {'State': 'Order'})
					data['products'] = self.db.get_products(menu, with_id=True)
				else:
					if data['data'].startswith('Sortby'):
						self.db.set_user_last_menu(upd['user_id'], {'Page': 1, 'Sort': data['data'][6:]})
					elif data['data'].startswith('FilterCategory'):
						self.db.set_user_last_menu(upd['user_id'], {'Page': 1, 'Filter': data['data'][14:].replace('_', ' ')})
					elif data['data'] in ['Clear', 'CancelToProduct']:
						self.db.set_user_last_menu(upd['user_id'], 'clear')
					elif data['data'].startswith('OrderProdId'):
						product = self.db.get_product_detail(data['data'][11:])
						caption = '*' + product[1] + '*\n\n*Price:* ' + '{:0,.0f}'.format(product[2]) + ' \n*Description:* ' + product[4] + '\n\nHow many?'
						self.api.send_product(upd['user_id'], product, caption)
					elif data['data'].startswith('OrderProdOkId'):
						prod_id, pcs = data['data'][13:].split('pcs')
					elif data['data'] in ['Prev', 'Next']:
						last_page = int(self.db.get_user_last_menu(upd['user_id'])['Page'])
						if data['data'] == 'Prev' and last_page > 1:
							self.db.set_user_last_menu(upd['user_id'], {'Page': last_page - 1})
						elif data['data'] == 'Next':
							self.db.set_user_last_menu(upd['user_id'], {'Page': last_page + 1})
					menu = self.db.get_user_last_menu(upd['user_id'])
					text = self.db.get_products(menu)
				self.api.edit_message(text, data)
			elif data['data'].startswith('AddToCart') and data['data'].endswith('More'):
				self.db.set_user_last_menu(upd['user_id'], {'State': data['data']})
				prod = data['text'].split('\n')[0]
				text = 'How many *' + prod + '* do you want?'
				self.api.delete_message(data)
				self.api.send_message(upd['user_id'], text, 'NONE')
			elif data['data'].startswith('AddToCart'):
				prod_id, quantity = data['data'][9:].split('pcs')
				self.db.add_cart(upd['user_id'], prod_id, quantity)
				self.api.delete_message(data)
				self.api.send_message(upd['user_id'], MESSAGE['added_cart'], 'MAIN')
			elif data['data'].startswith('EditCartId'):
				item = self.db.get_cart_detail(data['data'][10:])
				caption = '*' + item[1] + '*\n\n*Price:* ' + '{:0,.0f}'.format(item[2]) + ' \n*Description:* ' + item[4] + '\n*Quantity:* ' + str(item[5])
				self.api.delete_message(data)
				self.api.send_product(upd['user_id'], item, caption)
			elif data['data'] == 'EditCart':
				text = 'Edit item on cart:'
				data['cart'] = self.db.get_cart(upd['user_id'], type='option')
				self.api.edit_message(text, data)
			elif data['data'].startswith('RemoveCart'):
				self.db.remove_cart(data['data'][10:])
				text = self.db.get_cart(upd['user_id'])
				self.api.delete_message(data)
				self.api.send_message(upd['user_id'], text, 'CART')
			elif data['data'].startswith('UpdateCart') and data['data'].endswith('More'):
				self.db.set_user_last_menu(upd['user_id'], {'State': data['data']})
				prod = data['text'].split('\n')[0]
				text = 'How many *' + prod + '* do you want?'
				self.api.delete_message(data)
				self.api.send_message(upd['user_id'], text, 'NONE')
			elif data['data'].startswith('UpdateCart'):
				item_id, quantity = data['data'][10:].split('pcs')
				self.db.update_cart(item_id, quantity)
				text = self.db.get_cart(upd['user_id'])
				self.api.delete_message(data)
				self.api.send_message(upd['user_id'], text, 'CART')
			elif data['data'] == 'Checkout':
				self.api.answer_callback(data)
				self.api.send_message(upd['user_id'], MESSAGE['ask_location'], 'CHECKOUT')
			elif data['data'] == 'CancelCheckout':
				text = self.db.get_cart(upd['user_id'])
				self.api.delete_message(data)
				self.api.send_message(upd['user_id'], text, 'CART')
			elif data['data'] == 'ProcessCheckout':
				self.api.answer_callback(data)
				self.db.add_order(upd['user_id'])
				self.api.send_message(upd['user_id'], MESSAGE['added_order'], 'MAIN')