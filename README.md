# Odong2Bot
Telegram chatbot for online shop

<p align="center">
  <img src="demo/demo.gif" height="500"><br/>
  <i>Odong2Bot</i>
</p>

This bot pretend to be FMCG online shop, user can see list of product, order, and checkout.
You can try it on [@Odong2bot](https://t.me/Odong2bot).
Here are some of the features:
- Register user (automatically when start chating with bot)
- See list of Product
- Sort, Filter, and Search Product
- See list of item in Cart
- Edit and Remove item in Cart
- Checkout Order
- Send Location and auto detect address (reverse geocode from [OpenStreetMap](https://www.openstreetmap.org/))
- See Historical Transaction
- See Today's Promo

I use Python and Flask to serve webhook from Telegram API. Receive update, translate intent, and handle response.
For interact with Telegram, i use requests package directly to Telegram API without using some wrapper package.
I don't know that Telegram wrapper package like [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) exists. If i know erlier, i would like to use it from the start.


## Dependences
- [Flask](https://github.com/pallets/flask), for building web service
- [requests](https://github.com/psf/requests), for sending HTTP request to Telegram API
- [python-dotenv](https://github.com/theskumar/python-dotenv), for store and load secret key like token and password
- [PyMySQL](https://github.com/PyMySQL/PyMySQL), connector to mysql database
- [zappa](https://github.com/Miserlou/Zappa), easy build and deploy web service to serverless Service like AWS Lambda


## How to deploy
[Here](demo/installation.md) step by step how I deploy this bot on AWS Lambda.

## License
[MIT License](LICENSE)