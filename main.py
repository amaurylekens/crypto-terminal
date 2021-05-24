import time
import logging
import datetime
import configparser

import numpy as np
import pandas as pd
from rich import print
import tweepy
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from binance.client import Client

logger = logging.getLogger()

# Loading keys from config file
config = configparser.ConfigParser()
config.read_file(open('./secret.cfg'))
binance_api_key = config.get('BINANCE', 'ACTUAL_API_KEY')
binance_secret_key = config.get('BINANCE', 'ACTUAL_SECRET_KEY')

client = Client(binance_api_key, binance_secret_key)


def create_twitter_api(config):
    consumer_key = config.get("TWITTER", "CONSUMER_KEY")
    consumer_secret = config.get("TWITTER", "CONSUMER_SECRET")
    access_token_key = config.get("TWITTER", "ACCESS_TOKEN_KEY")
    access_token_secret = config.get("TWITTER", "ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api


class StreamListener(tweepy.StreamListener):

    def __init__(self, api):
        self.api = api
        self.me = api.me()
        self.buffer = []

    def on_status(self, tweet):x
        self.buffer.append({"username": tweet.user.name, "text": tweet.text})

    def on_error(self, status):
        print("Error detected")



twitter_api = create_twitter_api(config)

tweets_listener = StreamListener(twitter_api)

stream = tweepy.Stream(twitter_api.auth, tweets_listener)
stream.filter(track=["DOGE"], languages=["fr", "en"])

print("hello")

def get_tickers(symbols: list, client):

    """
    Return last prices for a list of symbols.

    :param symbols: list - list of symbols
    :return: list - list with the prices for each symbols.
    """

    tickers = []
    for symbol in symbols:
        ticker = client.get_ticker(symbol=symbol)
        ticker = {
            "symbol": symbol,
            "price": ticker["lastPrice"],
            "price_change_percent": ticker["priceChangePercent"]
        }
        tickers.append(ticker)
    return tickers


def generate_tickers_table(tickers) -> Table:
    """Make a new table."""
    table = Table(title="Tickers")
    table.add_column("Symbol")
    table.add_column("Price")
    table.add_column("24H")

    for ticker in tickers:
        color_percent = "green" if float(ticker["price_change_percent"]) > 0 else "red"
        table.add_row(
            f"{ticker['symbol']}",
            f"{str(ticker['price'])}",
            f"[bold {color_percent}]{str(ticker['price_change_percent'])}[/bold {color_percent}]"
        )
    return table


def generate_portfolio_table(account_infos, tickers):

    usd_values = {ticker["symbol"].replace("USDT", ""): ticker["price"] for ticker in tickers}
    table = Table(title="Portfolio")
    table.add_column("Asset")
    table.add_column("Quantity")
    table.add_column("USD")

    balances = account_infos["balances"]
    balances = [balance for balance in balances if float(balance["free"]) > 0]
    total_balance = 0
    for i, balance in enumerate(balances):
        table.add_row(
            f"{balance['asset']}",
            f"[purple]{round(float(balance['free']), 6)}[/purple]",
            f"{round(float(balance['free'])*float(usd_values[balance['asset']]), 6)}",
            end_section=(i == len(balances)-1)
        )
        total_balance += float(balance['free'])*float(usd_values[balance['asset']])
    table.add_row("[bold] TOTAL [/bold]", "", f"{round(total_balance, 6)}")
    return table




def generate_layout(client, tweets):

    tickers = get_tickers(["DOGEUSDT", "BTCUSDT", "ETHUSDT"], client)
    tickers_table = generate_tickers_table(tickers)

    account_infos = client.get_account()
    portfolio_table = generate_portfolio_table(account_infos, tickers)

    layout = Layout()
    layout.split_column(
        Layout(name="upper"),
        Layout(name="lower")
    )
    layout["upper"].split_row(
        Layout(tickers_table),
        Layout(portfolio_table)
    )
    tweets = (f"{tweet['username']}: {tweet['text']} \n" for tweet in tweets)
    Layout["lower"].update(
        tweets
    )

    return layout

"""
tweets = tweets_listener.buffer
print(tweets)
layout = generate_layout(client, tweets)


with Live(layout, refresh_per_second=4) as live:
    for _ in range(40):
        time.sleep(0.4)
        live.update(generate_layout(client))"""

