# Odong2Bot
Telegram chatbot for online shop

This bot pretend to be FMCG online shop, user can see list of product, order, and checkout.
Here are some of the features:
- Register user (automatically when start chating with bot)
- See list of Product
- Sort, Filter, and Search Product
- See list of item in Cart
- Edit and Remove item in Cart
- Checkout Order
- Send Location for delivery and add Note
- See Historical Transaction
- See Today's Promo

I use Python and Flask to serve webhook from Telegram API. Receive update, translate intent, and handle response.
For interact with Telegram, i use pure python directly to Telegram API without using some wrapper package.
I don't know that Telegram wrapper package like [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) exists. If i know erlier, i would like to use it from the start.


## How to deploy
Here are step by step how i deploy this bot to my Free Tier AWS Lambda from Ubuntu machine:

First, get your `AWS Access Key ID` and `AWS Secret Access Key` from AWS IAM Service
Then configure AWS Account from your local
```
pip3 install awscli
aws configure
```
fill AWS Access Key ID, AWS Secret Access Key, Default region name (like `us-east-1`), and Default output format (like `json`)

Clone this repository
```
mkdir bot
cd bot
git clone https://github.com/irfanchahyadi/Odong2Bot.git
```

Set up Environment
```
pip install virtualenv
cd Odong2Bot
python3 -m venv venv
source venv/bin/activate
```

Install required tools
```
pip3 install --no-cache-dir -r requirements.txt
```
**This bot require :**
- [Flask](https://github.com/pallets/flask), for building web service
- [requests](https://github.com/psf/requests), for sending HTTP request to Telegram API
- [python-dotenv](https://github.com/theskumar/python-dotenv), for storing secret key like token and password
- [PyMySQL](https://github.com/PyMySQL/PyMySQL), connector to mysql database
- [zappa](https://github.com/Miserlou/Zappa), easy build and deploy web service to serverless Service like AWS Lambda 
I use `--no-cache-dir` option to avoid MemoryError when installing zappa on my t2.micro EC2 with 1 Gb Memory.