from binance.client import Client
import configparser

# Loading keys from config file
config = configparser.ConfigParser()
config.read_file(open('./secret.cfg'))
api_key = config.get('BINANCE', 'ACTUAL_API_KEY')
secret_key = config.get('BINANCE', 'ACTUAL_SECRET_KEY')


client = Client(api_key, secret_key)  # To change endpoint URL for test account

infos = client.get_account()

print(infos)