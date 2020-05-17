## How to deploy using AWS Lambda
Here are step by step how i deploy this bot to my Free Tier AWS Lambda from Ubuntu machine:

First, get your `AWS Access Key ID` and `AWS Secret Access Key` from AWS IAM Service.

Then configure AWS Account from your local
```
pip3 install awscli
aws configure
```
fill AWS Access Key ID, AWS Secret Access Key, Default region name (like `us-east-1`), and Default output format (like `json`)

then, provide `.env` file inside `/src` folder contain
```python
TOKEN =                   # bot token get it from BotFather
URL =                     # this for set webhook, receive after success deploy it to AWS Lambda (read below)
MYSQL_USERNAME =          # create when configuring mysql (read below)
MYSQL_PASSWORD =          # create when configuring mysql (read below)
MYSQL_DATABASE =          # create when configuring mysql (read below)
MYSQL_HOSTNAME =          # mysql server hostname
```

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

I use `--no-cache-dir` option to avoid MemoryError when installing zappa on my t2.micro EC2 with only 1 Gb Memory.

Before  deploy it, we need to configure mysql to enable remote access. You can skip this step if you have done it before.

Exit from virtual environment, then open and edit my.cnf
```
deactivate
sudo nano /etc/mysql/my.cnf
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
exit
sudo service mysql restart
```

Edit Inbound Rule
- Go to your EC2 console
- Click security group on your instance
- Edit Inbound rule
- Add MYSQL/Aurora type in port 3306 from anywhere

Activate again venv environment, then configure zappa
```
source venv/bin/activate
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

Set webhook & reset database
- `url/set_webhook` to set webhook to Telegram API
- `url/reset_db` to activate and reset database (optional)