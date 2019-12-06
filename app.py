
"""
App File
Author: Irfan Chahyadi
Source: github.com/irfanchahyadi/Odong2Bot
"""

from flask import Flask, request, jsonify
from src.bot_handler import Handler
import os

app = Flask(__name__)
handler = Handler()

@app.route('/', methods=['GET', 'POST'])
def webhook():
	if request.method == 'POST':
		req = request.get_json()
		upd = handler.extract_updates(req)
		handler.handle(upd)
	return 'ok'

@app.route('/set_webhook')
def set_webhook():
	res = handler.set_webhook()
	data = {'result': res}
	return jsonify(data)


if __name__ == "__main__":
	app.run(threaded=True)


# USING WHILE LOOP
# import time

# if __name__ == '__main__':
# 	handler = Handler()
# 	last_update_id = 0
# 	print('Listening to: ' + handler.get_me())
# 	while True:
# 		jsn = handler.get_updates(last_update_id)
# 		if jsn['ok']:
# 			for msg in jsn['result']:
# 				upd = handler.extract_updates(msg)
# 				last_update_id = max(last_update_id, upd['update_id']) + 1
# 				handler.handle(upd)
# 		time.sleep(1)