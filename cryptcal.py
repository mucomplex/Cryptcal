#!/bin/python3
import os
import sys
import argparse
import requests
import json

#Config
set_api = True

class crypto_currency:
    #default parameters
    def __init__(self,symbol,usdt):
        self.symbol = symbol.upper()
        self.value  = self.symbol_price()
        self.volume = usdt / self.value

    #getting price function
    def symbol_price(self):
        r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol='+ self.symbol)
        value = json.loads(r.text)
        print("current symbol : " + value["symbol"])
        print("current price  : " + value["price"])
        return float(value["price"])

    #risk calculation
    def percentage_risk(self):
        net_profit = (self.value * 0.02)
        net_loss   = (self.value * 0.01)
        set_profit = self.value + net_profit 
        set_loss   = self.value - net_loss 
        print('profit set : ' + str(set_profit))
        print('loss set   : ' + str(set_loss))
        print('profit volume available   : $' + str(net_profit * self.volume))
        print('loss will be              : $' + str(net_loss * self.volume))


parser = argparse.ArgumentParser()
parser.add_argument('symbol',nargs='+',help='place pair symbol e.g btcusdt .')
parser.add_argument('usdt',nargs='+',type=float,help='usdt amount you want to trade.')
args = parser.parse_args()
results = crypto_currency(args.symbol[0],args.usdt[0])
results.percentage_risk()

