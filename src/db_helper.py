
"""
DB Helper
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

import sqlite3, os

class dbHelper():
	def __init__(self, init_setup=False, db_name='bot.db'):
		self.db_name = db_name
		if init_setup:
			if db_name in os.listdir('src'):
				os.remove('src/' + self.db_name)
		self.con = sqlite3.connect('src/' + self.db_name)
		self.cur = self.con.cursor()
		if init_setup:
			self.initial_setup()

	def add_cart(self, user_id, prod_id, quantity):
		last_quantity = self.cur.execute('SELECT quantity FROM cart_items WHERE user_id = (?) AND prod_id =(?)', [user_id, prod_id]).fetchone()
		if last_quantity:
			stmt = 'UPDATE cart_items SET quantity = (?) WHERE user_id = (?) AND prod_id = (?)'
			args = (last_quantity[0] + quantity, user_id, prod_id)
		else:
			stmt = 'INSERT INTO cart_items (user_id, prod_id, quantity) VALUES (?,?,?)'
			args = (user_id, prod_id, quantity)
		self.con.execute(stmt, args)
		self.con.commit()


	def initial_setup(self):
		sql_script = """
			CREATE TABLE products (
				prod_id INT,
				prod VARCHAR(50),
				category VARCHAR(50),
				price FLOAT,
				stock INT,
				image_id VARCHAR(50),
				description VARCHAR(255));

			CREATE TABLE users (
				user_id INT,
				username VARCHAR(50),
				join_date DATETIME);

			CREATE TABLE cart_items (
				cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INT,
				prod_id INT,
				quantity INT);
			
			CREATE TABLE orders (
				order_id INT,
				user_id INT,
				created_date DATETIME,
				total_price FLOAT,
				lat_delivery INT,
				long_delivery INT,
				address_delivery VARCHAR(255));

			CREATE TABLE order_items (
				order_id INT,
				prod_id INT,
				quantity INT,
				price_each FLOAT);

			INSERT INTO products VALUES
				(1, 'BANGO MANIS REFIL 600ML', 'Bahan Memasak', 24600, 827, 'AgADBQADx6cxGzzjAAFULg_aWPgG56pBTsoyAARk3-t4a85mVEY1AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (2, 'BIMOLI POUCH 1 LTR', 'Bahan Memasak', 15100, 213, 'AgADBQADyKcxGzzjAAFUOEA87JSbTEb5SMoyAAQn-fwDT0Qh9Dk3AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (3, 'CADBURY DAIRY MILK CASHEW NUT 65G', 'Snack', 14200, 94, 'AgADBQADyqcxGzzjAAFUIfGS5vYTrFOYRMoyAAQNQA8HZodpl-g0AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (4, 'DAIA PUTIH POWDER DET 900G', 'Sabun', 14300, 42, 'AgADBQADy6cxGzzjAAFUDkPiia3DpoqjRsoyAARFZz25YH-hJqc2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (5, 'MAMA LEMON XTRA CLN FRESH LEMON PCH 800ML', 'Sabun', 13700, 55, 'AgADBQADzKcxGzzjAAFUS80ftCtm5kpcLsoyAATR2xi8fwTcG-8SAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (6, 'MOLTO ALL IN 1 BLUE POUCH 900ML', 'Sabun', 25300,55, 'AgADBQADzacxGzzjAAFUN6HutX6DJyQcHsoyAATxWyyc2mYfab4RAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (7, 'RINSO ANTI NODA 900G', 'Sabun', 17700,17, 'AgADBQADzqcxGzzjAAFUh0UxUGe1XcsfLcoyAAQ2IZ-z1nO_850SAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (8, 'SUNLIGHT LEMON NEW POUCH 800ML', 'Sabun', 13700,83, 'AgADBQADz6cxGzzjAAFUabzQkXibhMsmR8oyAAR6HWKw9XSmwfY4AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (9, 'VIXAL PEMB PORS BIRU 800ML','Sabun', 14700,232, 'AgADBQAD0KcxGzzjAAFUZyaZ4dHQyYLPH8oyAAQTAZ-As1OBW1IUAwABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.'),
                (10, 'WIPOL CLASSIC PINE POUCH 800ML', 'Sabun', 14000,356, 'AgADBQAD0acxGzzjAAFUqYZkRdsCp1i1VsoyAAQmcH75p5a-m7g2AgABAg', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas iaculis tristique imperdiet.');
			"""
		self.cur.executescript(sql_script)