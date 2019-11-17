
"""
Main File
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

from src.db_helper import dbHelper
from src.bot_api import botAPI
from src.bot_message import MESSAGE
import time

if __name__ == '__main__':
	db = dbHelper(init_setup=True)
	api = botAPI()
	last_update_id = 0
	while True:
		jsn = api.get_updates(last_update_id)
		if jsn['ok']:
			for msg in jsn['result']:
				update_id, type, date, user_id, username, data = api.extract_updates(msg)
				last_update_id = max(last_update_id, update_id) + 1
				if type == 'text' and data == '/start':
					db.add_user(user_id, username)
					keyb = api.build_keyboard('MAIN')
					api.send_message(user_id, MESSAGE['welcome'], keyb)
		print(last_update_id)
		time.sleep(1)