import csv
import re
import os
import requests as req
import datetime as dt
import time as tm
from bs4 import BeautifulSoup as bs
import pandas as pd

class Asset:
    """A simple asset class."""

    def __init__(self, name):
        self.name = name
        self.buy = 0
        self.sell = 0
        self.spread = 0
        self.time = []
        self.source = []

    def download_data(self, source, Session):
        html_data = bs(Session.sess.get(
            source, headers=Session.HEADERS).content, 'html.parser')
        print(str(dt.datetime.now()) + ": Data downloaded.")

        html_data = html_data.find(
            class_='cleanList floatList clearFix quoteBar ')

        buy_html = str(html_data.find_all(
            class_='buyPrice SText bold')).replace(',', '.')
        # print buy_html

        sell_html = str(html_data.find_all(
            class_='sellPrice SText bold')).replace(',', '.')
        # print sell_html

        time_html = str(html_data.find_all(class_='updated SText bold'))
        # print time_html

        buy_price = float(re.findall('">(.*)</', buy_html)[0])
        sell_price = float(re.findall('">(.*)</', sell_html)[0])
        time_price = re.findall('">(.*)</', time_html)[0]

        self.source = source
        self.time = pd.to_datetime(time_price)
        self.buy = buy_price
        self.sell = sell_price
        self.spread = sell_price - buy_price

    def write_data(self, path):
        with open(path, 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([self.time, self.buy, self.sell, self.spread])
            print(str(dt.datetime.now()) + ": Data saved.")


def working_hours(current, opening, closing):
    """A function that checks if the current time is inside the working hours."""
    if (current.isoweekday() < 6) and (opening <= current.time() <= closing):
        return True


if __name__ == '__main__':
    tm.sleep(3)
    url = 'https://www.avanza.se'
    
    source = "https://www.avanza.se/borshandlade-produkter/warranter-torg/om-warranten.html/718871/mini-l-tesla-ava-28"  # webpage where
    path = './TSLA.csv'  # local path to store data
    tesla = Asset("TSLA")  # initiate asset instance

    exchange_opening_time = dt.time(9)
    exchange_closing_time = dt.time(17, 30)

    print("UTC: " + str(dt.datetime.utcnow()))  # current universal time

    scrape_freq = 10  # frequency in seconds
    scrapping_status = True

    time_stamp = pd.to_datetime(dt.datetime.now())
    while scrapping_status:
        current_local_time = dt.datetime.now()
        if working_hours(current_local_time, exchange_opening_time, exchange_closing_time):
            try:
                tesla.download_data(source, avanza)
                if tesla.time != time_stamp:
                	tesla.write_data(path)
                	time_stamp = tesla.time
            except:
                print("Data download failed.")
                pass
            tm.sleep(scrape_freq)

        else:
            print("Now it is " +
                  current_local_time.strftime(
                      '%A, %x, %X') + " and the market is closed. The scrapping will continue as soon as the market opens.")
            current_plus_hour = current_local_time + dt.timedelta(hours=1)
            current_plus_minute = current_local_time + dt.timedelta(minutes=1)
            if working_hours(current_plus_minute, exchange_opening_time, exchange_closing_time):
                tm.sleep(1)
            elif working_hours(current_plus_hour, exchange_opening_time, exchange_closing_time):
                tm.sleep(60)
            else:
                tm.sleep(3600)
