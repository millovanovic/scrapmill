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


if __name__ == '__main__':
    print "UTC: " + str(dt.datetime.utcnow())  # current universal time

    scrape_freq = 10 # frequency in seconds
    scrapping_status = True
    while scrapping_status:

        current_local_time = dt.datetime.now()

        exchange_opening_time = dt.time(9)
        exchange_closing_time = dt.time(17, 30)

        if (current_local_time.isoweekday() < 6) and (exchange_opening_time <= current_local_time.time() <= exchange_closing_time):
            source = "https://www.avanza.se/borshandlade-produkter/warranter-torg/om-warranten.html/718871/mini-l-tesla-ava-28"
            path = './TSLA.csv'
            tesla = Asset("TSLA")
            tesla.download_data(source)
            tesla.write_data(path)

            tm.sleep(scrape_freq)
