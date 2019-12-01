
"""
DB Helper
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

import sqlite3, os, json
from datetime import datetime

CLEAR_MENU = {'State': '', 'Sort': '', 'Filter': '', 'Search':'', 'Page': 1, 'Address': '', 'Lat': '', 'Lon': '', 'Note': ''}

class dbHelper():
	def __init__(self, init_setup=False, db_name='bot.db'):
		self.db_name = db_name
		self.n_prod = 5
		if init_setup:
			if db_name in os.listdir('src'):
				os.remove('src/' + self.db_name)
		self.con = sqlite3.connect('src/' + self.db_name)
		self.cur = self.con.cursor()
		if init_setup:
			self.initial_setup()

	def add_cart(self, user_id, prod_id, quantity):
		last_quantity = self.cur.execute('SELECT quantity FROM cart_items WHERE user_id = (?) AND prod_id =(?);', [user_id, prod_id]).fetchone()
		if last_quantity:
			sql = 'UPDATE cart_items SET quantity = (?) WHERE user_id = (?) AND prod_id = (?);'
			args = (last_quantity[0] + int(quantity), user_id, prod_id)
		else:
			sql = 'INSERT INTO cart_items (user_id, prod_id, quantity) VALUES (?,?,?);'
			args = (user_id, prod_id, int(quantity))
		self.con.execute(sql, args)
		self.con.commit()

	def add_user(self, user_id, username):
		check_user = self.cur.execute('SELECT COUNT(*) FROM users WHERE user_id = (?);', (user_id,)).fetchone()[0]
		if not check_user:
			sql = 'INSERT INTO users (user_id, username, join_date, last_menu) VALUES (?,?,?,?);'
			args = (user_id, username, datetime.now(), json.dumps(CLEAR_MENU))
			self.con.execute(sql, args)
			self.con.commit()
	
	def get_user_last_menu(self, user_id):
		last_menu = self.cur.execute('SELECT last_menu FROM users WHERE user_id = (?);', (str(user_id), )).fetchone()[0]
		return json.loads(last_menu)

	def set_user_last_menu(self, user_id, menu):
		if menu == 'clear':
			menu = CLEAR_MENU
		last_menu = self.get_user_last_menu(user_id)
		last_menu.update(menu)
		new_menu = json.dumps(last_menu)
		sql = 'UPDATE users SET last_menu = (?) WHERE user_id = (?);'
		args = (new_menu, user_id)
		self.con.execute(sql, args)
		self.con.commit()

	def get_product_category(self):
		sql = 'SELECT DISTINCT category FROM products;'
		categories = self.con.execute(sql)
		return categories.fetchall()

	def get_product_detail(self, prod_id):
		sql = "SELECT prod_id, prod, price, image_id, description FROM products WHERE prod_id = '{}'".format(prod_id)
		return self.con.execute(sql).fetchone()

	def get_products(self, menu=CLEAR_MENU, with_id=False):
		args = None
		sql = 'SELECT prod, price, prod_id FROM products'
		
		if menu['Filter'] != '' and menu['Search'] != '':
			sql += " WHERE category = '{}' AND prod like '%{}%'".format(menu['Filter'], menu['Search'])
		elif menu['Filter'] != '':
			sql += " WHERE category = '{}'".format(menu['Filter'])
		elif menu['Search'] != '':
			sql += " WHERE prod like '%{}%'".format(menu['Search'])
		else:
			pass

		d = {'HighestPrice': 'price DESC', 'LowestPrice': 'price ASC', 'NameA-Z': 'prod ASC', 'NameZ-A': 'prod DESC'}
		if menu['Sort'] != '':
			sql += " ORDER BY " + d[menu['Sort']]
		
		sql += " LIMIT " + str(self.n_prod)

		if int(menu['Page']) != 1:
			offset = (int(menu['Page']) - 1) * self.n_prod
			sql += " OFFSET " + str(offset)

		list_product = self.con.execute(sql)
		
		if with_id:
			message = []
			for row in list_product:
				message.append([row[0], row[1], row[2]])
		else:
			message = ['*List Product*\n\[Sort: {}]  \[Filter: {}]  \[Search: {}]  \[Page: {}]\n'.format(menu['Sort'], menu['Filter'], menu['Search'], menu['Page'])]
			for row in list_product:
				message.append(row[0] + ' - ' + '{:0,.0f}'.format(row[1]))
			message = '\n'.join(message)
		return message

	def get_cart(self, user_id, type='message'):
		sql = 'SELECT c.quantity, p.prod, p.price, c.cart_item_id, p.prod_id FROM cart_items c INNER JOIN products p ON p.prod_id=c.prod_id WHERE c.user_id = {}'.format(user_id)
		list_cart = self.con.execute(sql)
		items = list_cart.fetchall()

		if type == 'list':
			message = items
		elif type == 'option':
			message = []
			for item in items:
				message.append([('' if item[0]>=10 else ' ') + str(item[0]) + ' x ' + item[1] + ' @ {:0,.0f}'.format(item[2]), item[3]])
		elif type == 'message':
			if len(items) > 0:
				message = ['*Your Cart:*']
				total = 0
				for item in items:
					message.append(('' if item[0]>=10 else ' ') + str(item[0]) + ' x ' + item[1] + ' @ {:0,.0f}'.format(item[2]))
					total += item[0] * item[2]
			
				message = '\n'.join(message)
				message += '\n*Total: Rp ' + '{:0,.0f}'.format(total) + '*'
			else:
				message = 'Your Cart is empty, please order in Product List.'
		return message

	def get_cart_detail(self, item_id):
		sql = "SELECT p.prod_id, p.prod, p.price, p.image_id, p.description, c.quantity, c.cart_item_id FROM cart_items c INNER JOIN products p ON p.prod_id=c.prod_id WHERE cart_item_id = '{}'".format(item_id)
		return self.con.execute(sql).fetchone()
	
	def remove_cart(self, item_id):
		sql = 'DELETE FROM cart_items WHERE cart_item_id = {};'.format(item_id)
		self.con.execute(sql)
		self.con.commit()

	def update_cart(self, item_id, quantity):
		sql = 'UPDATE cart_items SET quantity = {} WHERE cart_item_id = {}'.format(quantity, item_id)
		self.con.execute(sql)
		self.con.commit()

	def clear_cart(self, user_id):
		sql = 'DELETE FROM cart_items WHERE user_id = {};'.format(user_id)
		self.con.execute(sql)
		self.con.commit()

	def add_order(self, user_id):
		menu = self.get_user_last_menu(user_id)
		cart = self.get_cart(user_id, type='list')
		total = sum([i[0]*i[2] for i in cart])
		sql = 'INSERT INTO orders (user_id, created_date, total_price, lat_delivery, lon_delivery, address_delivery, note) VALUES (?,?,?,?,?,?,?);'
		args = (user_id, datetime.now(), total, menu['Lat'], menu['Lon'], menu['Address'], menu['Note'])
		order_id = self.con.execute(sql, args).lastrowid
		self.con.commit()
		sql2 = 'INSERT INTO order_items (order_id, prod_id, quantity, price_each) VALUES (?,?,?,?)'
		args2 = [(order_id, i[4], i[0], i[2]) for i in cart]
		self.con.executemany(sql2, args2)
		self.con.commit()
		self.clear_cart(user_id)
		self.set_user_last_menu(user_id, 'clear')

	def get_order(self, user_id):
		sql = 'SELECT order_id, created_date, total_price, address_delivery, note FROM orders WHERE user_id = {} ORDER BY created_date DESC LIMIT 5'.format(user_id)
		list_order = self.con.execute(sql)
		message = 'Showing 5 last order:\n'
		for idx, order in enumerate(list_order):
			sql2 = 'SELECT o.quantity, p.prod, o.price_each FROM order_items o INNER JOIN products p ON p.prod_id=o.prod_id WHERE order_id = {}'.format(order[0])
			list_item = self.con.execute(sql2).fetchall()
			if idx != 0:
				message += '\n\n============  #####  ============\n'
			order_at = datetime.strptime(order[1], '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%y %H:%M:%S')
			message += '\n*Order at:* ' + order_at
			message += '\n\n*List item:*'
			for item in list_item:
				message += '\n' + ('' if item[0]>=10 else ' ') + str(item[0]) + ' x ' + item[1] + ' @ {:0,.0f}'.format(item[2])
			message += '\n*Total:* {:0,.0f}'.format(order[2])
			message += '\n\n*Delivery address:* ' + order[3]
			message += '\n\n*Note:* ' + order[4]
		return message

	def get_promo(self):
		sql = 'SELECT image_id, caption FROM active_promo;'
		return self.con.execute(sql).fetchall()

	def initial_setup(self):
		sql_script = """
			CREATE TABLE products (
				prod_id INTEGER PRIMARY KEY,
				prod VARCHAR(50),
				category VARCHAR(50),
				price FLOAT,
				stock INT,
				image_id VARCHAR(50),
				description VARCHAR(255));

			CREATE TABLE users (
				user_id INTEGER PRIMARY KEY,
				username VARCHAR(50),
				join_date DATETIME,
				last_menu VARCHAR(50));

			CREATE TABLE cart_items (
				cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INT,
				prod_id INT,
				quantity INT);
			
			CREATE TABLE orders (
				order_id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INT,
				created_date DATETIME,
				total_price FLOAT,
				lat_delivery INT,
				lon_delivery INT,
				address_delivery VARCHAR(255),
				note VARCHAR(255));

			CREATE TABLE order_items (
				order_id INT,
				prod_id INT,
				quantity INT,
				price_each FLOAT);

			CREATE TABLE active_promo (
				promo_id INT,
				caption VARCHAR(255),
				image_id VARCHAR(50));

			INSERT INTO products VALUES
				(1, 'Bango Manis Refil 600ml', 'Ingredients', 24600, 827, 'AgADBQADx6cxGzzjAAFULg_aWPgG56pBTsoyAARk3-t4a85mVEY1AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (2, 'Bimoli Pouch 1L', 'Ingredients', 15100, 213, 'AgADBQADyKcxGzzjAAFUOEA87JSbTEb5SMoyAAQn-fwDT0Qh9Dk3AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (3, 'Cadbury Dairy Milk 65gr', 'Snack', 14200, 94, 'AgADBQADyqcxGzzjAAFUIfGS5vYTrFOYRMoyAAQNQA8HZodpl-g0AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (4, 'Daia Putih 900gr', 'Detergent Soap', 14300, 42, 'AgADBQADy6cxGzzjAAFUDkPiia3DpoqjRsoyAARFZz25YH-hJqc2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (5, 'Mama Lemon Pouch 800ml', 'Detergent Soap', 13700, 55, 'AgADBQADzKcxGzzjAAFUS80ftCtm5kpcLsoyAATR2xi8fwTcG-8SAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (6, 'Molto All In 1 Blue 900ml', 'Detergent Soap', 25300, 55, 'AgADBQADzacxGzzjAAFUN6HutX6DJyQcHsoyAATxWyyc2mYfab4RAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (7, 'Rinso Anti Noda 900gr', 'Detergent Soap', 17700, 17, 'AgADBQADzqcxGzzjAAFUh0UxUGe1XcsfLcoyAAQ2IZ-z1nO_850SAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (8, 'Sunlight Lemon 800ml', 'Detergent Soap', 13700, 83, 'AgADBQADz6cxGzzjAAFUabzQkXibhMsmR8oyAAR6HWKw9XSmwfY4AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (9, 'Vixal Pembersih Porselen 800ml','Detergent Soap', 14700, 232, 'AgADBQAD0KcxGzzjAAFUZyaZ4dHQyYLPH8oyAAQTAZ-As1OBW1IUAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (10, 'Wipol Classic Pine 800ml', 'Detergent Soap', 14000, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(11, 'Silver Queen Original', 'Snack', 15900, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(12, 'Gulaku Premium 1kg', 'Ingredients', 12500, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(13, 'Bogasari Tepung Terigu 1kg', 'Ingredients', 11900, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(14, 'Mayumi Mayonnaise 100ml', 'Ingredients', 7900, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(15, 'La Fonte Bolognese 315gr', 'Ingredients', 19500, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(16, 'Lays Nori Seaweed 55gr', 'Snack', 9200, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(17, 'Pringles Original 107gr', 'Snack', 25000, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(18, 'Oreo Box Original', 'Snack', 21500, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(19, 'Fisherman Friend Citrus 25gr', 'Snack', 15000, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(20, 'Pocky Chocolate 47gr', 'Snack', 8500, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(21, 'KitKat Bar 35gr', 'Snack', 10500, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(22, 'Snickers', 'Snack', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(23, 'Cornetto Classic', 'Snack', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(24, 'Magnum Infinity', 'Snack', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(25, 'Blueband 200gr', 'Ingredients', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(26, 'Kraft Cheddar 175gr', 'Ingredients', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(27, 'Sambal ABC', 'Ingredients', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(28, 'Indomie Goreng', 'Instant Food', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(29, 'Pop Mie Pedas Cup', 'Instant Food', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(30, 'Super Bubur Instan', 'Instant Food', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(31, 'Nissin Top Ramen', 'Instant Food', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(32, 'Quaker Instant Oatmeal', 'Instant Food', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(33, 'Koko Krunch Chocolate', 'Instant Food', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(34, 'Chocolatos', 'Drinks', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(35, 'Good Days Cappuccino', 'Drinks', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(36, 'White Koffie Original', 'Drinks', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(37, 'Nestle Milo 220gr', 'Drinks', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(38, 'Nestcafe Classic', 'Drinks', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(39, 'Nestea Lemon Tea 715gr', 'Drinks', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(40, 'Max Tea Tarik 125gr', 'Drinks', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				
                ;

			INSERT INTO active_promo VALUES
				(1, "New year's promo", 'AgADBQADrKcxG9P_8Ffuiv20WVyDs-YzyjIABDa7HDuAONv62jACAAEC')
			"""
		self.cur.executescript(sql_script)