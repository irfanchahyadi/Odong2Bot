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
- Send Location and auto detect address (reverse geocode from [openstreetmap](https://www.openstreetmap.org/))
- See Historical Transaction
- See Today's Promo

I use Python and Flask to serve webhook from Telegram API. Receive update, translate intent, and handle response.
For interact with Telegram, i use pure python directly to Telegram API without using some wrapper package.
I don't know that Telegram wrapper package like [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) exists. If i know erlier, i would like to use it from the start.


## Environment variable
provide `.env` file inside `/src` folder contain
```python
TOKEN =                   # bot token given from BotFather
URL =                     # this for set webhook, receive after success deploy it to AWS Lambda (read below)
MYSQL_USERNAME =          # create when configuring mysql (read below)
MYSQL_PASSWORD =          # create when configuring mysql (read below)
MYSQL_DATABASE =          # create when configuring mysql (read below)
MYSQL_HOSTNAME =          # mysql server hostname
```


## How to deploy
Further will be just technical stuff.

Here are step by step how i deploy this bot to my Free Tier AWS Lambda from Ubuntu machine:

First, get your `AWS Access Key ID` and `AWS Secret Access Key` from AWS IAM Service.

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
- [python-dotenv](https://github.com/theskumar/python-dotenv), for store and load secret key like token and password
- [PyMySQL](https://github.com/PyMySQL/PyMySQL), connector to mysql database
- [zappa](https://github.com/Miserlou/Zappa), easy build and deploy web service to serverless Service like AWS Lambda

I use `--no-cache-dir` option to avoid MemoryError when installing zappa on my t2.micro EC2 with only 1 Gb Memory.

Before  deploy it, we need to configure mysql to enable remote access. You can skip this step if you have done it before.

Exit from virtual environment, then open and edit my.cnf
```
deactivate
nano /etc/mysql/my.cnf
```

Replace this line, or add if not exists
```
[mysqld]
bind-address = 0.0.0.0
```

Restart mysql service and allow port 3306 to use by mysql
```
sudo service mysql restart
sudo ufw allow 3306/tcp
```

Login to mysql as root, create new database, add user bot, then restart mysql again
```
mysql -u root -p
CREATE DATABASE odong2bot;
GRANT ALL PRIVILEGES ON odong2bot.* TO bot@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
sudo service mysql restart
```

Configure zappa
```
zappa init
```
Basically, just press enter to each question, the default configuration should be good enough. Then
```
zappa deploy dev
```
If this command run successfully, you will get the url where your lambda service deploy.
Copy it to URL in `.env` file, then update it with command
```
zappa update
```