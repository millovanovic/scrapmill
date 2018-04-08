import csv
import re
import requests as req
import os.path as osp
import datetime as dt
import time as tm
from bs4 import BeautifulSoup as bs


class Asset:
    """A simple asset class."""

    def __init__(self, name):
        self.name = name
        self.buy = 0
        self.sell = 0
        self.spread = 0
        self.time = []
        self.source = []

    def download_data(self, source):
        html_data = bs(req.get(source).content, 'html.parser')
        print str(dt.datetime.now()) + ': Data downloaded.'

        buy_html = str(html_data.find_all(
            class_='buyPrice SText bold')).replace(',', '.')
        sell_html = str(html_data.find_all(
            class_='sellPrice SText bold')).replace(',', '.')
        time_html = str(html_data.find_all(class_='updated SText bold'))

        buy_price = float(re.findall('">(.*)</', buy_html)[0])
        sell_price = float(re.findall('">(.*)</', sell_html)[0])
        time_price = re.findall('">(.*)</', time_html)[0]

        self.source = source
        self.time = time_price
        self.buy = buy_price
        self.sell = sell_price
        self.spread = sell_price - buy_price

    def write_data(self, path):
        with open(path, 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([self.time, self.buy, self.sell, self.spread])
            print str(dt.datetime.now()) + ': Data saved.'


def working_hours(current, opening, closing):
    """A function that checks if the current time is inside the working hours."""
    if (current.isoweekday() < 6) and (opening <= current.time() <= closing):
        return True


if __name__ == '__main__':
    # webpage where live data can be found
    source = "https://www.avanza.se/borshandlade-produkter/warranter-torg/om-warranten.html/718871/mini-l-tesla-ava-28"
    path = './TSLA.csv'  # local path to store data
    tesla = Asset("TSLA")  # initiate asset instance

    exchange_opening_time = dt.time(9)
    exchange_closing_time = dt.time(17, 30)

    print "UTC: " + str(dt.datetime.utcnow())  # current universal time

    scrape_freq = 10  # frequency in seconds
    scrapping_status = True
    while scrapping_status:
        current_local_time = dt.datetime.now()
        if working_hours(current_local_time, exchange_opening_time, exchange_closing_time):
            tesla.download_data(source)
            tesla.write_data(path)
            tm.sleep(scrape_freq)

        else:
            print "Now it is " + \
                current_local_time.strftime(
                    '%A, %x, %X') + " and the market is closed. The scrapping will continue as soon as the market opens."
            current_plus_hour = current_local_time + dt.timedelta(hours=1)
            current_plus_minute = current_local_time + dt.timedelta(minutes=1)
            if working_hours(current_plus_minute, exchange_opening_time, exchange_closing_time):
                tm.sleep(1)
            elif working_hours(current_plus_hour, exchange_opening_time, exchange_closing_time):
                tm.sleep(60)
            else:
                tm.sleep(3600)
