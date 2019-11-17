
"""
Main File
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

from src.db_helper import dbHelper
from src.bot_api import botAPI

if __name__ == '__main__':
	db = dbHelper(init_setup=True)
	api = botAPI()
	api.get_updates()