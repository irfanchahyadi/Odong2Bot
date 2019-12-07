
"""
DB Helper
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

import pymysql, json, dotenv, os
from datetime import datetime

CLEAR_MENU = {'State': '', 'Sort': '', 'Filter': '', 'Search':'', 'Page': 1, 'Address': '', 'Lat': '', 'Lon': '', 'Note': ''}
dotenv.load_dotenv()

class dbHelper():
	def __init__(self, init_setup=False, db_name='bot.db'):
		user = os.getenv('MYSQL_USERNAME')
		pwd  = os.getenv('MYSQL_PASSWORD')
		db   = os.getenv('MYSQL_DATABASE')
		host = os.getenv('MYSQL_HOSTNAME')
		self.n_prod = 10
		self.con = pymysql.connect(user=user, password=pwd, database=db, host=host, autocommit=True)

	def add_cart(self, user_id, prod_id, quantity):
		with self.con.cursor() as cur:
			cur.execute('SELECT quantity FROM cart_items WHERE user_id = %s AND prod_id = %s;', (user_id, prod_id))
			last_quantity = cur.fetchone()
		
		if last_quantity:
			sql = 'UPDATE cart_items SET quantity = %s WHERE user_id = %s AND prod_id = %s;'
			args = (last_quantity[0] + int(quantity), user_id, prod_id)
		else:
			sql = 'INSERT INTO cart_items (user_id, prod_id, quantity) VALUES (%s,%s,%s);'
			args = (user_id, prod_id, int(quantity))
		with self.con.cursor() as cur:
			cur.execute(sql, args)

	def add_user(self, user_id, username):
		with self.con.cursor() as cur:
			cur.execute('SELECT COUNT(*) FROM users WHERE user_id = %s;', (user_id))
			check_user = cur.fetchone()[0]

		if not check_user:
			sql = 'INSERT INTO users (user_id, username, join_date, last_menu) VALUES (%s,%s,%s,%s);'
			args = (user_id, username, datetime.now(), json.dumps(CLEAR_MENU))
			with self.con.cursor() as cur:
				cur.execute(sql, args)
	
	def get_user_last_menu(self, user_id):
		with self.con.cursor() as cur:
			cur.execute('SELECT last_menu FROM users WHERE user_id = %s;', (str(user_id)))
			last_menu = cur.fetchone()[0]
		return json.loads(last_menu)

	def set_user_last_menu(self, user_id, menu):
		if menu == 'clear':
			menu = CLEAR_MENU
		last_menu = self.get_user_last_menu(user_id)
		last_menu.update(menu)
		new_menu = json.dumps(last_menu)
		sql = 'UPDATE users SET last_menu = %s WHERE user_id = %s;'
		args = (new_menu, user_id)
		with self.con.cursor() as cur:
			cur.execute(sql, args)

	def get_product_category(self):
		with self.con.cursor() as cur:
			cur.execute('SELECT DISTINCT category FROM products;')
		return cur.fetchall()

	def get_product_detail(self, prod_id):
		with self.con.cursor() as cur:
			cur.execute("SELECT prod_id, prod, price, image_id, description FROM products WHERE prod_id = %s", (prod_id))
		return cur.fetchone()

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
		
		with self.con.cursor() as cur:
			cur.execute(sql)
		list_product = cur.fetchall()
		
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
		with self.con.cursor() as cur:
			cur.execute('SELECT c.quantity, p.prod, p.price, c.cart_item_id, p.prod_id FROM cart_items c INNER JOIN products p ON p.prod_id=c.prod_id WHERE c.user_id = %s', (user_id))
		items = cur.fetchall()

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
		with self.con.cursor() as cur:
			cur.execute("SELECT p.prod_id, p.prod, p.price, p.image_id, p.description, c.quantity, c.cart_item_id FROM cart_items c INNER JOIN products p ON p.prod_id=c.prod_id WHERE cart_item_id = %s", (item_id))
		return cur.fetchone()
	
	def remove_cart(self, item_id):
		with self.con.cursor() as cur:
			cur.execute('DELETE FROM cart_items WHERE cart_item_id = %s;', (item_id))

	def update_cart(self, item_id, quantity):
		with self.con.cursor() as cur:
			cur.execute('UPDATE cart_items SET quantity = %s WHERE cart_item_id = %s', (quantity, item_id))

	def clear_cart(self, user_id):
		with self.con.cursor() as cur:
			cur.execute('DELETE FROM cart_items WHERE user_id = %s;', (user_id))

	def add_order(self, user_id):
		menu = self.get_user_last_menu(user_id)
		cart = self.get_cart(user_id, type='list')
		total = sum([i[0]*i[2] for i in cart])
		sql = 'INSERT INTO orders (user_id, created_date, total_price, lat_delivery, lon_delivery, address_delivery, note) VALUES (%s,%s,%s,%s,%s,%s,%s);'
		args = (user_id, datetime.now(), total, menu['Lat'], menu['Lon'], menu['Address'], menu['Note'])
		with self.con.cursor() as cur:
			cur.execute(sql, args)
			order_id = cur.lastrowid

		sql2 = 'INSERT INTO order_items (order_id, prod_id, quantity, price_each) VALUES (%s,%s,%s,%s)'
		args2 = [(order_id, i[4], i[0], i[2]) for i in cart]
		print(args2)
		with self.con.cursor() as cur:
			cur.executemany(sql2, args2)
		self.clear_cart(user_id)
		self.set_user_last_menu(user_id, 'clear')

	def get_order(self, user_id):
		with self.con.cursor() as cur:
			cur.execute('SELECT order_id, created_date, total_price, address_delivery, note FROM orders WHERE user_id = %s ORDER BY created_date DESC LIMIT 5', (user_id))
		list_order = cur.fetchall()
		
		if len(list_order) > 0:
			message = 'Showing 5 last order:\n'
			for idx, order in enumerate(list_order):
				with self.con.cursor() as cur:
					cur.execute('SELECT o.quantity, p.prod, o.price_each FROM order_items o INNER JOIN products p ON p.prod_id=o.prod_id WHERE order_id = %s', (order[0]))
				list_item = cur.fetchall()
				
				if idx != 0:
					message += '\n\n============  #####  ============\n'
				order_at = order[1].strftime('%d/%m/%Y  %H:%M')
				message += '\n*Order at:*  ' + order_at
				message += '\n\n*List item:*'
				for item in list_item:
					message += '\n' + ('' if item[0]>=10 else ' ') + str(item[0]) + ' x ' + item[1] + ' @ {:0,.0f}'.format(item[2])
				message += '\n*Total:* {:0,.0f}'.format(order[2])
				message += '\n\n*Delivery address:* ' + order[3]
				message += '\n\n*Note:* ' + order[4]

		else:
			message = "You haven't ordered yet. You can order from Product List."
		return message

	def get_promo(self):
		with self.con.cursor() as cur:
			cur.execute('SELECT image_id, caption FROM active_promo;')
		return cur.fetchall()

	def reset_db(self):
		drop_script = """
			DROP TABLE IF EXISTS products;
			DROP TABLE IF EXISTS users;
			DROP TABLE IF EXISTS cart_items;
			DROP TABLE IF EXISTS orders;
			DROP TABLE IF EXISTS order_items;
			DROP TABLE IF EXISTS active_promo;
			"""
		sql_script = """
			CREATE TABLE products (
				prod_id INTEGER PRIMARY KEY,
				prod VARCHAR(50),
				category VARCHAR(50),
				price FLOAT,
				stock INT,
				image_id VARCHAR(100),
				description VARCHAR(255));

			CREATE TABLE users (
				user_id INTEGER PRIMARY KEY,
				username VARCHAR(50),
				join_date DATETIME,
				last_menu VARCHAR(255));

			CREATE TABLE cart_items (
				cart_item_id INTEGER PRIMARY KEY AUTO_INCREMENT,
				user_id INT,
				prod_id INT,
				quantity INT);
			
			CREATE TABLE orders (
				order_id INTEGER PRIMARY KEY AUTO_INCREMENT,
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
				image_id VARCHAR(100));

			INSERT INTO products VALUES
				(1, 'Bango Manis Refil 600ml', 'Ingredients', 24600, 356, 'AgADBQADx6cxGzzjAAFULg_aWPgG56pBTsoyAARk3-t4a85mVEY1AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (2, 'Bimoli Pouch 1L', 'Ingredients', 15100, 356, 'AgADBQADyKcxGzzjAAFUOEA87JSbTEb5SMoyAAQn-fwDT0Qh9Dk3AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (3, 'Cadbury Dairy Milk 65gr', 'Snack', 14200, 356, 'AgADBQADyqcxGzzjAAFUIfGS5vYTrFOYRMoyAAQNQA8HZodpl-g0AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (4, 'Daia Putih 900gr', 'Detergent Soap', 14300, 356, 'AgADBQADy6cxGzzjAAFUDkPiia3DpoqjRsoyAARFZz25YH-hJqc2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (5, 'Mama Lemon Pouch 800ml', 'Detergent Soap', 13700, 356, 'AgADBQADzKcxGzzjAAFUS80ftCtm5kpcLsoyAATR2xi8fwTcG-8SAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (6, 'Molto All In 1 Blue 900ml', 'Detergent Soap', 25300, 356, 'AgADBQADzacxGzzjAAFUN6HutX6DJyQcHsoyAATxWyyc2mYfab4RAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (7, 'Rinso Anti Noda 900gr', 'Detergent Soap', 17700, 356, 'AgADBQADzqcxGzzjAAFUh0UxUGe1XcsfLcoyAAQ2IZ-z1nO_850SAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (8, 'Sunlight Lemon 800ml', 'Detergent Soap', 13700, 356, 'AgADBQADz6cxGzzjAAFUabzQkXibhMsmR8oyAAR6HWKw9XSmwfY4AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (9, 'Vixal Pembersih Porselen 800ml','Detergent Soap', 14700, 356, 'AgADBQAD0KcxGzzjAAFUZyaZ4dHQyYLPH8oyAAQTAZ-As1OBW1IUAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (10, 'Wipol Classic Pine 800ml', 'Detergent Soap', 14000, 356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(11, 'Silver Queen Original', 'Snack', 15900, 356, 'AgADBQADN6kxG1fXKFdf-k6ZdGdntzaPAjMABAEAAwIAA20AA6UdBgABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(12, 'Gulaku Premium 1kg', 'Ingredients', 12500, 356, 'AgADBQADKKkxG2y3KFeNX7uWd-qNJocmGzMABAEAAwIAA20AA5cLAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(13, 'Bogasari Tepung Terigu 1kg', 'Ingredients', 11900, 356, 'AgADBQADKakxG2y3KFeLGoA7MGXgDJS2JTMABAEAAwIAA20AA4R1AAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(14, 'Mayumi Mayonnaise 100ml', 'Ingredients', 7900, 356, 'AgADBQADKqkxG2y3KFf71CLmVcskVGskGzMABAEAAwIAA20AA48MAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(15, 'La Fonte Bolognese 315gr', 'Ingredients', 19500, 356, 'AgADBQADK6kxG2y3KFcUouCYy5ATwGuDAjMABAEAAwIAA20AAxc7BgABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(16, 'Lays Nori Seaweed 55gr', 'Snack', 9200, 356, 'AgADBQADLKkxG2y3KFf7bFm78yIvl06tJTMABAEAAwIAA20AA0B1AAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(17, 'Pringles Original 107gr', 'Snack', 25000, 356, 'AgADBQADLakxG2y3KFecAfVPjYoP7WzBJTMABAEAAwIAA20AA510AAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(18, 'Oreo Box Original', 'Snack', 21500, 356, 'AgADBQADLqkxG2y3KFfJW-Sl185ZLXs2GzMABAEAAwIAA20AA7oIAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(19, 'Fisherman Friend Citrus 25gr', 'Snack', 15000, 356, 'AgADBQADL6kxG2y3KFebrR1XGhcRbfIrGzMABAEAAwIAA20AAyYLAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(20, 'Pocky Chocolate 47gr', 'Snack', 8500, 356, 'AgADBQADMKkxG2y3KFcAAdUT1dOyD4sNKRszAAQBAAMCAANtAAOPBwEAARYE', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(21, 'KitKat Bar 35gr', 'Snack', 10500, 356, 'AgADBQADMakxG2y3KFdVmsaG5MMQ0U64JTMABAEAAwIAA20AA0pyAAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(22, 'Snickers 51gr', 'Snack', 9900, 356, 'AgADBQADMqkxG2y3KFdYppEwrupqQtbDJTMABAEAAwIAA20AA5N3AAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(23, 'Cornetto Classic 82ml', 'Snack', 5000, 356, 'AgADBQADOakxG1fXKFcUAAEwns7lGktHhgIzAAQBAAMCAANtAAMHKgYAARYE', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(24, 'Magnum Infinity 3 Bars', 'Snack', 35000, 356, 'AgADBQADOqkxG1fXKFd8QabH-V30Ote1JTMABAEAAwIAA20AAxR2AAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(25, 'Blueband 200gr', 'Ingredients', 7600, 356, 'AgADBQADPKkxG1fXKFf9uiBHaBe9QLSBAjMABAEAAwIAA20AA9I2BgABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(26, 'Kraft Cheddar 75gr', 'Ingredients', 22500, 356, 'AgADBQADM6kxG2y3KFdysRzw2KvIhRqQAjMABAEAAwIAA20AA9wtBgABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(27, 'Sambal ABC 335ml', 'Ingredients', 13900, 356, 'AgADBQADNKkxG2y3KFfJSdA5EQkrJqqJAjMABAEAAwIAA20AA8I0BgABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(28, 'Indomie Goreng 29gr', 'Instant Food', 3200, 356, 'AgADBQADNakxG2y3KFcnVPe0hVg8s_khGzMABAEAAwIAA20AA18LAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(29, 'Pop Mie Pedas Cup 57gr', 'Instant Food', 4600, 356, 'AgADBQADPakxG1fXKFfUukjja8dlEHQ2GzMABAEAAwIAA20AA_0MAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(30, 'Super Bubur Instan 51gr', 'Instant Food', 3500, 356, 'AgADBQAD8KkxG2cuKVfMxl2VBA6MvSwtGzMABAEAAwIAA20AA6wKAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(31, 'Nissin Top Ramen', 'Instant Food', 12800, 356, 'AgADBQADNqkxG2y3KFdFc-kBCteMiBI3GzMABAEAAwIAA20AA9QJAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(32, 'Quaker Instant Oatmeal 800gr', 'Instant Food', 46900, 356, 'AgADBQADN6kxG2y3KFeLibB5mlNI4tcyGzMABAEAAwIAA20AA3EKAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(33, 'Koko Krunch Chocolate 170gr', 'Instant Food', 19500, 356, 'AgADBQADOKkxG2y3KFfM9FnCnvn_mFivJTMABAEAAwIAA20AA_V2AAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(34, 'Chocolatos 4pcs', 'Drinks', 8900, 356, 'AgADBQADOakxG2y3KFc6YPA68PWMTogxGzMABAEAAwIAA20AA1gKAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(35, 'Good Days Cappuccino 5x25gr', 'Drinks', 9400, 356, 'AgADBQADOqkxG2y3KFci-n7YoKGJxTGjJTMABAEAAwIAA20AA0N0AAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(36, 'White Koffie Original 10x20gr', 'Drinks', 9900, 356, 'AgADBQADO6kxG2y3KFdd0khWHoWREN41GzMABAEAAwIAA20AA9EIAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(37, 'Nestle Milo 220gr', 'Drinks', 26800, 356, 'AgADBQADPKkxG2y3KFfiZNF54xDwQfm7JTMABAEAAwIAA20AA251AAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(38, 'Nestcafe Classic 50gr', 'Drinks', 15300, 356, 'AgADBQADPakxG2y3KFdIGhqMLTE3uAetJTMABAEAAwIAA20AA_B0AAIWBA', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(39, 'Nestea Lemon Tea 715gr', 'Drinks', 39800, 356, 'AgADBQADPqkxG2y3KFdZ6wZ5t0ZMlY8oGzMABAEAAwIAA20AA1AHAQABFgQ', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
				(40, 'Max Tea Tarik 5x25gr', 'Drinks', 11500, 356, 'AgADBQADP6kxG2y3KFeHNgWTQqdSRqbBJTMABAEAAwIAA20ABHUAAhYE', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.');

			INSERT INTO active_promo VALUES
				(1, "New year's promo", 'AgADBQADrKcxG9P_8Ffuiv20WVyDs-YzyjIABDa7HDuAONv62jACAAEC')
			"""
		with self.con.cursor() as cur:
			for sql in drop_script.split(';') + sql_script.split(';'):
				if len(sql.strip()) > 0:
					cur.execute(sql)