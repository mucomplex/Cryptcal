#!/bin/python3

'''

Author : mucomplex
requirement : 
pip install python-binance
pip install colored

'''

import os
import sys
import argparse
import requests
import json
import time
from colored import fg,bg,attr
from binance.client import Client
from binance.exceptions import BinanceAPIException


#Config
api_key=""
api_secret=""
sleep_timer = 0.5


class crypto_currency:
    #default parameters
    def __init__(self,symbol,usdt):
        self.client = Client(api_key,api_secret)
        self.usdt_asset()
        self.symbol = symbol.upper()
        self.value  = self.symbol_price()
        #Volume error handling.
        if(usdt > self.value and self.value > 0.1):
            self.volume = round(usdt / self.value,1)
        elif(self.value < 0.1):
            self.volume = round(usdt / self.value,0)
        else:
            self.volume = round(usdt / self.value,4)
        print("Volume available : " + str(self.volume))
        
    def usdt_asset(self):
        print('--------------------------------')
        balance = self.client.get_asset_balance(asset='USDT')
        print("USDT balance amount : %s$%s%s" % (fg(10),balance["free"],attr(0)))

    def buy_at_current_price(self):
        try:
            self.client.order_limit_buy(symbol=self.symbol,quantity=self.volume,price=self.value)
        except BinanceAPIException as e:
            print(e.message)



    #getting price function
    def symbol_price(self):
        r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol='+ self.symbol)
        value = json.loads(r.text)
        current_price = round(float(value["price"]),5)
        print("current symbol : " + value["symbol"])
        print("current price  : %s$%s%s" % (fg(11),str(current_price),attr(0)))
        return current_price

    #risk calculation
    def percentage_risk(self):
        net_profit = round((self.value * 0.02),5)
        net_loss   = round((self.value * 0.01),5)
        set_profit = round(self.value + net_profit,5)
        set_loss   = round(self.value - net_loss,5)
        print('profit set : %s%s%s' % (fg(10),str(set_profit),attr(0)))
        print('loss set   : %s%s%s' % (fg(9),str(set_loss),attr(0)))
        print('profit volume available (2R)   : $%s' %(str(net_profit * self.volume)))
        print('loss will be            (1R)   : $%s' %(str(net_loss * self.volume)))
        print('--------------------------------')


#define argparse
parser = argparse.ArgumentParser()
parser.add_argument('symbol',nargs='+',help='place pair symbol e.g btcusdt .')
parser.add_argument('usdt',nargs='+',type=float,help='usdt amount you want to trade.')
parser.add_argument('--execute',help='It either "buy" or "sell".')
parser.add_argument('--repeate',help='keep it running.')
args = parser.parse_args()

#main function
def main():
    results = crypto_currency(args.symbol[0],args.usdt[0])
    if(args.execute == 'buy'):
        print('\n---------- buy status ----------')
        results.buy_at_current_price()
        results.usdt_asset()

    results.percentage_risk()

#loop case
while(args.repeate == 'true'):
    main()
    time.sleep(sleep_timer)

#non-loop
if(args.repeate == None):
    main()
