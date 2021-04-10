#!/bin/python3
import os
import sys
import argparse

class crypto_currency:
    def __init__(self,value):
        self.value = value

    def percentage_risk(self):
        net_profit = (self.value * 0.02)
        net_loss   = (self.value * 0.01)
        set_profit = self.value + net_profit 
        set_loss   = self.value - net_loss 
        print('profit set : ' + str(set_profit))
        print('loss set   : ' + str(set_loss))
        print('profit for 10 trade   : ' + str(net_profit * 10))


parser = argparse.ArgumentParser()
parser.add_argument('value',nargs='+',type=float,help='usdt amount you want to trade.')
args = parser.parse_args()
results = crypto_currency(args.value[0])
results.percentage_risk()

