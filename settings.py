import logging
import configparser

#logging setting
logging.basicConfig(format='[%(levelname)s %(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

#load api_id and api_hash form config
config = configparser.ConfigParser()
config.read("config.ini")


api_id = int(config['Telegram']['api_id'])
api_hash = str(config['Telegram']['api_hash'])
phone =  config['Telegram']['phone']
username = config['Telegram']['username']
