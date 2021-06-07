#!/bin/python3

'''

Author : mucomplex
requirement : 
pip install python-binance
pip install python-binance==0.7.5
pip install colored

'''

'''
#v2
need to do:
    OCO trading.
    if OCO success, need to review back

#v1 not use anymore.
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
from binance.enums import *


#Config binance
api_key     =""
api_secret  =""
#Config taapi
api_taapi   =""
exchange    ="binance"
interval    ="1m"

#Default config
sleep_timer = 0.1
No_trading_per_coin = 1
robots_testing = True

'''
e.g main function defined.
results = crypto_currency(args.symbol[0],args.usdt[0])
results.overall_results()
results.pull_user_data()

results.define_buy()
results.bot_buy_check()
results.bot_sell_check()


'''
class crypto_currency:

    def __init__(self,symbol,usdt):
        #setting API
        self.client = Client(api_key,api_secret)
        self.symbol_taapi = (symbol + "/USDT").upper()
        self.symbol = self.symbol_taapi.replace('/','')

        #user info
        self.balance = 0

        #user input defined.
        self.usdt = usdt

        #define results
        self.No_of_Trade = 0
        self.Win         = 0
        self.Lose        = 0

        #define bband value
        self.valueUpperBand  =0 
        self.valueMiddleBand =0
        self.valueLowerBand  =0 

        #profit_count
        self.total_profit = 0

        #pre-defined risk
        self.entry_price= 0
        self.stop_loss  = 0
        self.net_profit = 0 
        self.net_loss   = 0 
        self.set_profit = 0 
        self.set_loss   = 0 

        #pre-defined risk 2
        self.buy_price      = 0
        self.profit_price   = 0
        self.med_price      = 0
        self.loss_price     = 0
        self.trade_unit     = 0

        #previous_candle_settings
        self.candle1_open   = 0 
        self.candle1_close  = 0 
        self.candle1_high   = 0 
        self.candle1_low    = 0 

        #robots testing buy & sell
        self.robots_is_buy_price_enable = False
        self.colored_buy_price = False

        #bot setting
        self.Trading = []

    def pull_user_data(self):
        self.usdt_asset()
        self.get_prev_candle()
        self.current_price = self.symbol_price()
        self.percentage_risk()
        self.unit = self.unit_check()


    def overall_results(self):
        print('%sWin         : %s%s' %(fg(10),attr(0),self.Win))
        print('%sLose        : %s%s' %(fg(9),attr(0),self.Lose))
        print('%sTrade       : %s%s' %(fg(117),attr(0),self.No_of_Trade))
        print('%sProfit      : %s%s' %(fg(165),attr(0),self.total_profit))
        print('%sPer-Trade   : %s%s' %(fg(43),attr(0),len(self.Trading)))
        #make the buy colored if success execute.
        if(self.colored_buy_price == True):
            print('%sBuy price   : %s%s%s%s' %(fg(117),attr(0),fg(43),self.buy_price,attr(0)))
        else:
            print('%sBuy price   : %s%s' %(fg(117),attr(0),self.buy_price))
        print('%sprofit price: %s%s' %(fg(10),attr(0),self.profit_price))
        print('%smed price   : %s%s' %(fg(11),attr(0),self.med_price))
        print('%sloss price  : %s%s' %(fg(9),attr(0),self.loss_price))
        print('%strade unit  : %s%s' %(fg(43),attr(0),self.trade_unit))

    def define_buy(self):
        #indicators
        self.hammer             = self.pattern_hammer()
        self.invertedhammer     = self.pattern_invertedhammer()
        self.engulfing          = self.pattern_engulfing()
        self.morningstar        = self.pattern_morningstar()
        self.ema20_buy          = self.get_ema20_check_buy()
        self.sma50_buy          = self.get_sma50_check_buy()
        self.sma100_buy         = self.get_sma100_check_buy()
        self.rsi_buy_uptrend    = self.get_rsi_check_buy_uptrend()
        self.rsi_buy_downtrend  = self.get_rsi_check_buy_downtrend()
        self.bbands_buy         = self.get_bbands_check_buy()
        self.macd_buy           = self.get_macd_check_buy()
        self.macd_p4            = self.get_macd_check_buy_past4()
        self.qstick             = self.pattern_qstick()
        self.qstick25           = self.pattern_qstick25()

        #special case indicator
        self._3whitesoldiers    = self.pattern_3whitesoldiers()


    #--------------------------------------------------------------- important part -------------------------------------------------------

    #buy bot completed!.
    def bot_buy_check(self):
        '''
        '''
        if(

                ((self.hammer == True or self.invertedhammer == True or self.engulfing == True or self.morningstar == True or self._3whitesoldiers) and
                (((
                    # entry price must greater than ema20 and 3% below ema20.
                    (self.current_price >= self.ema20_buy and self.current_price >= (self.ema20_buy - (self.ema20_buy * 0.03))) or
                    # entry price must either 3% greater and lower sma50.
                    ((self.sma50_buy + (self.sma50_buy   *0.03)) >= self.current_price and self.current_price >= (self.sma50_buy  - (self.sma50_buy * 0.03))) or 
                    # entry price must either 3% greater and lower sma100.
                    ((self.sma100_buy + (self.sma100_buy *0.03)) >= self.current_price and self.current_price >= (self.sma100_buy - (self.sma100_buy * 0.03))) or
                #lower bband greater than entry price.
                (self.bbands_buy == True)
                )) or
                #downtrend buy 10% below 20 ema.(where incase the candle drop to much.
                ((self.ema20_buy - (self.ema20_buy * 0.1)) >= self.current_price and self.qstick == False)) and 
                #either rsi,macd.
                #rsi uptrend set to 35
                #((self.rsi_buy_uptrend == True and self.qstick25==True) or
                ((self.rsi_buy_uptrend == True) or
                #rsi downtrend set to 25
                #(self.rsi_buy_downtrend == True and self.qstick25==False) or
                (self.rsi_buy_downtrend == True) or
                 #(self.macd_buy == True and self.macd_p4 == True)
                (self.macd_buy == True)
                 )
                ) or
                
                #special case indicator here.
                #Three with soldiers should be with downtrend.
                (self._3whitesoldiers == True) or
                #morningstar
                (self.morningstar == True)
                ):


            if(float(self.balance) > self.usdt or robots_testing == True):
                #defined 1 trade per coin.
                if(len(self.Trading) < No_trading_per_coin):
                    Trading_Dict = {
                        "Id": self.No_of_Trade,
                        "buy_price": self.entry_price,
                        "high_price": self.set_profit,
                        "med_price": self.valueMiddleBand,
                        "low_price": self.set_loss,
                        "unit_amount" : self.unit,
                        }

                    #define the price.
                    self.buy_price      = self.entry_price
                    self.profit_price   = self.set_profit 
                    self.med_price      = self.valueMiddleBand
                    self.loss_price     = self.set_loss
                    self.trade_unit     = self.unit

                    #add buy to list.
                    self.Trading.append(Trading_Dict)
                    self.No_of_Trade += 1 


    def bot_sell_check(self):
        if(self.current_price == 0):
            return 0
        for sell_check in self.Trading:
            #just to immitate if robots successfully buy,and price is not zero.
            # self.robots_is_buy_price_enable is to check if the bot already buy once.
            if(self.current_price > sell_check['buy_price'] and (self.robots_is_buy_price_enable == False)):
                self.colored_buy_price = True
                self.robots_is_buy_price_enable = True
                '''
                #execute buy order.
                for decimal in range(6,-1,-1):
                    if(decimal == 0):
                        valid_unit_amount = int(sell_check['unit_amount'])
                    else:
                        valid_unit_amount = round(sell_check['unit_amount'],decimal)

                    if(self.order_buy_price(valid_unit_amount,self.current_price) != False):
                        break
                    else:
                        print('%sAttempt to buy.%s' %(fg(43),attr(0)))

                #execute sell order.
                # minus unit_amount * 0.002 is trading fee need by binance.
                valid_unit_amount = sell_check["unit_amount"] - (sell_check["unit_amount"] * 0.002)
                for decimal in range(6,-1,-1):
                    if(decimal == 0):
                        valid_unit_amount = int(valid_unit_amount)
                    else:
                        valid_unit_amount = round(valid_unit_amount,decimal)

                    if(self.order_oco_sell_price(valid_unit_amount,sell_check["high_price"],sell_check["low_price"]) != False):
                        break
                    else:
                        print('%sAttempt to set sell execution. :( .%s' %(fg(200),attr(0)))
                '''

            if((self.current_price > sell_check['high_price']) and self.robots_is_buy_price_enable):
                self.colored_buy_price = False
                self.robots_is_buy_price_enable = False
                self.Win +=1
                self.total_profit += ((self.current_price - sell_check['buy_price']) * sell_check["unit_amount"])
                self.Trading.remove(sell_check)
                break


            if((self.current_price < sell_check['low_price']) and self.robots_is_buy_price_enable):
                self.colored_buy_price = False
                self.robots_is_buy_price_enable = False
                self.Lose +=1
                self.total_profit -= ((sell_check['buy_price'] - self.current_price) * sell_check["unit_amount"])
                self.Trading.remove(sell_check)
                break

            if(self.current_price <  sell_check['low_price']):
                self.colored_buy_price = False
                self.robots_is_buy_price_enable = False
                self.Trading.remove(sell_check)


    #--------------------------------------------------------------- important part -------------------------------------------------------
    #--------------------------------------------------------------- default function -----------------------------------------------------


    '''
    !DO NOT TOUCH, CODE ALREADY COMPLETE.
    '''
    #unit is check on the entry price, not on current Price.
    def unit_check(self):
        #unit error handling.
        #check if usdt is larger than current price and 0.1
        if(self.usdt > self.entry_price and self.entry_price > 0.1):
                unit = round(self.usdt / self.entry_price,1)
        #check if current price less than 0.1
        elif(self.entry_price < 0.1):
                unit = round(self.usdt / self.entry_price,0)
        #check if current price larger than usdt.
        else:
                unit = round(self.usdt / self.entry_price,4)
        print("current unit: " + str(unit))
        return unit

    '''
    !DO NOT TOUCH, CODE ALREADY COMPLETE.
    '''
    def usdt_asset(self):
        try:
            balance = self.client.get_asset_balance(asset='USDT')
            self.balance = balance["free"]
            print("USDT balance: %s$%s%s" % (fg(220),balance["free"],attr(0)))
        except:
            print("USDT balance: Server reset.")

    '''
    !DO NOT TOUCH, CODE ALREADY COMPLETE.
    '''
    def order_buy_price(self,unit_quantity,unit_price):
        try:
            self.client.order_limit_buy(symbol=self.symbol,quantity=unit_quantity,price=unit_price)
            print('%sSuccessful buy!.%s' %(fg(43),attr(0)))
            return True
        except BinanceAPIException as e:
            #print(e.message)
            #print(e.code)
            #return e.code
            return False

    '''
    !DO NOT TOUCH, CODE ALREADY COMPLETE.
    '''
    def order_sell_price(self,unit_quantity,unit_price):
        try:
            self.client.order_limit_sell(symbol=self.symbol,quantity=unit_quantity,price=unit_price)
            return True
        except BinanceAPIException as e:
            #print(e.message)
            #print(e.code)
            #return e.code
            return False

    def order_oco_sell_price(self,unit_quantity,upper_price,lower_price):
        try:
            self.client.create_oco_order(
                symbol=self.symbol,
                side='sell',
                stopLimitTimeInForce=TIME_IN_FORCE_GTC,
                quantity=unit_quantity,
                price=upper_price,
                stopPrice=(lower_price + (lower_price * 0.001)),
                stopLimitPrice= lower_price
                )

            print('%sSell execution succeed. :) .%s' %(fg(200),attr(0)))
            return True

        except BinanceAPIException as e:
            #print(e.message)
            #print(e.code)
            #return e.code
            return False



    #getting price function
    def symbol_price(self):
        try:
            r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol='+ self.symbol)
            value = json.loads(r.text)
            current_price = round(float(value["price"]),5)
            print("symbol      : " + value["symbol"])
            print("curr price  : %s%s%s" % (fg(220),str(current_price),attr(0)))
            return current_price
        except:
            print("curr price  : %s%s%s" % (fg(11),"Not Available.",attr(0)))
            return 0

    '''
    DO NOT TOUCH,COMPLETE ALREADY.
    '''
    def get_prev_candle(self):
        endpoint = "https://api.taapi.io/candle"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'backtrack':1}
        try:
            response            = requests.get(url=endpoint,params = parameters)
            result              = json.loads(response.text)
            self.candle1_open   = result["open"] 
            self.candle1_close  = result["close"] 
            self.candle1_high   = result["high"] 
            self.candle1_low    = result["low"] 
        except:
            print("price       : %s%s%s" % (fg(11),"Not Available.",attr(0)))
            return 0

    '''
    DO NOT TOUCH, COMPLETE ALREADY.
    '''
    #risk calculation
    #0.0013 is gap on high and lower previous candle.
    def percentage_risk(self):
        self.entry_price    = round(self.candle1_high + (self.candle1_high * 0.0013),5)
        self.stop_loss      = round(self.candle1_low - (self.candle1_low * 0.0013),5)
        self.net_profit     = round(((self.entry_price - self.stop_loss) * 2),5)
        self.net_loss       = round((self.entry_price - self.stop_loss),5)
        self.set_profit     = round(self.entry_price + ((self.entry_price - self.stop_loss) * 2),5)
        self.set_loss       = self.stop_loss 

        print("entry price : %s" % (str(self.entry_price)))
        #disable,it may duplicate when successful buy.
        #print('profit set  : %s%s%s' % (fg(10),str(self.set_profit),attr(0)))
        #print('loss set    : %s%s%s' % (fg(9),str(self.set_loss),attr(0)))
        print('profit (2R) : $%s' %(round(self.net_profit * self.trade_unit,4)))
        print('loss   (1R) : $%s' %(round(self.net_loss * self.trade_unit,4)))

    #--------------------------------------------------------------- default function -----------------------------------------------------
    #--------------------------------------------------------------- default Api -------------------------------------------------------
    '''
    !DO NOT TOUCH QSTICK PATTERN, ALREADY COMPLETE.
    period is set 10 for per minutes.
    period 25 is to validate with sell price.
    '''
    def pattern_qstick(self):
        endpoint = "https://api.taapi.io/qstick"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'period':10}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result          = json.loads(response.text)
        except:
            return False
        if(result["value"] > 0):
                print('%s[+]qstick10 : Uptrend%s ' %(fg(10),attr(0)))
                return True
        else:
            print('%s[-]qstick10 : Downtrend%s ' %(fg(9),attr(0)))
            return False

    def pattern_qstick25(self):
        endpoint = "https://api.taapi.io/qstick"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'period':25}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result          = json.loads(response.text)
        except:
            return False
        if(result["value"] > 0):
                print('%s[+]qstick25 : Uptrend%s ' %(fg(10),attr(0)))
                return True
        else:
            print('%s[-]qstick25 : Downtrend%s ' %(fg(9),attr(0)))
            return False


    #--------------------------------------------------------------- default Api -------------------------------------------------------

    #--------------------------------------------------------------- buying mechanism --------------------------------------------------
    '''
    DO NOT TOUCH THE ALL SPECIAL INDICATOR, ALREADY COMPLETE.
    all pattern mechanism is set to previous 3 candle stick (backtracks 3) to match with MACD and RSI.
    '''
    def pattern_hammer(self):
        endpoint = "https://api.taapi.io/hammer"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'backtracks':3}
        try:
            response = requests.get(url=endpoint,params = parameters)
            results   = json.loads(response.text)
        except:
            return False
        for result in results:
            if(result["value"] == 100):
                print('%s[+]hammer   : Success%s ' %(fg(10),attr(0)))
                return True
        print('%s[-]hammer   : Failed%s ' %(fg(9),attr(0)))
        return False

    def pattern_invertedhammer(self):
        endpoint = "https://api.taapi.io/invertedhammer"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'backtracks':3}
        try:
            response = requests.get(url=endpoint,params = parameters)
            results   = json.loads(response.text)
        except:
            return False
        for result in results:
            if(result["value"] == 100):
                print('%s[+]Ihammer  : Success%s ' %(fg(10),attr(0)))
                return True
        print('%s[-]Ihammer  : Failed%s ' %(fg(9),attr(0)))
        return False

    def pattern_engulfing(self):
        endpoint = "https://api.taapi.io/engulfing"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'backtracks':3}
        try:
            response = requests.get(url=endpoint,params = parameters)
            results   = json.loads(response.text)
        except:
            return False
        for result in results:
            if(result["value"] == 100):
                print('%s[+]engulf   : Success%s ' %(fg(10),attr(0)))
                return True
        print('%s[-]engulf   : Failed%s ' %(fg(9),attr(0)))
        return False


    def pattern_morningstar(self):
        endpoint = "https://api.taapi.io/morningstar"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'backtracks':3}
        try:
            response = requests.get(url=endpoint,params = parameters)
            results   = json.loads(response.text)
        except:
            return False
        for result in results:
            if(result["value"] == 100):
                print('%s[+]ms       : Success%s ' %(fg(10),attr(0)))
                return True
        print('%s[-]ms       : Failed%s ' %(fg(9),attr(0)))
        return False


    def pattern_3whitesoldiers(self):
        endpoint = "https://api.taapi.io/3whitesoldiers"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'backtracks':3}
        try:
            response = requests.get(url=endpoint,params = parameters)
            results   = json.loads(response.text)
        except:
            return False
        for result in results:
            if(result["value"] == 100):
                print('%s[+]3ws      : Success%s ' %(fg(10),attr(0)))
                return True
            print('%s[-]3ws      : Failed%s ' %(fg(9),attr(0)))
            return False

    '''
    ! DO NOT TOUCH THE CODE, ALREADY COMPLETE.
    MACD is succeed when histogram is positive, MACD > signalMACD, and it still lower than 0
    -remove the comment to enable value display.

    macd past 3 is to make sure we not buy on high false positive value, as value MACD is set 0.1 higher then signal value.
    '''
    def get_macd_check_buy(self):
        endpoint = "https://api.taapi.io/macd"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result   = json.loads(response.text)
        except:
            return False
        if(result["valueMACDHist"] < 0 and ((result["valueMACD"] + abs(result["valueMACD"] * 0.1)) > result["valueMACDSignal"])):
            #print('%s[+]MACD %s : Success%s ' %(fg(10),round(result["valueMACDHist"],6),attr(0)))
            print('%s[+]MACD     : Success%s ' %(fg(10),attr(0)))
            return True
        else:
            #print('%s[-]MACD %s : Failed%s ' %(fg(9),round(result["valueMACDHist"],6),attr(0)))
            print('%s[-]MACD     : Failed%s ' %(fg(9),attr(0)))
            return False

    def get_macd_check_buy_past4(self):
        endpoint = "https://api.taapi.io/macd"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'backtrack':4}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result   = json.loads(response.text)
        except:
            return False
        if(result["valueMACDHist"] < 0):
            #print('%s[+]MACD_p4 %s : Success%s ' %(fg(10),round(result["valueMACDHist"],6),attr(0)))
            print('%s[+]MACD_p4  : Success%s ' %(fg(10),attr(0)))
            return True
        else:
            #print('%s[-]MACD_p4 %s : Failed%s ' %(fg(9),round(result["valueMACDHist"],6),attr(0)))
            print('%s[-]MACD_p4  : Failed%s ' %(fg(9),attr(0)))
            return False


    '''
    !DO NOT TOUCH THE CODE, ALREADY COMPLETE.
    Bollinger band defined.
    -disable the comment to show the value.
    '''
    def get_bbands_check_buy(self):
        endpoint = "https://api.taapi.io/bbands"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result   = json.loads(response.text)
        except:
            return False
        self.valueUpperBand     = round(result["valueUpperBand"],5)
        self.valueMiddleBand    = round(result["valueMiddleBand"],5)
        self.valueLowerBand     = round(result["valueLowerBand"],5)
        if(result["valueLowerBand"]  >= self.current_price):
            #print('%s[+]bbands %s : Success%s' %(fg(10),self.valueLowerBand,attr(0)))
            print('%s[+]bbands   : Success%s' %(fg(10),attr(0)))
            return True
        elif(result["valueMiddleBand"] > self.current_price):
            print('%s[=]bbands   : Normal%s ' %(fg(142),attr(0)))
            return False
        else:
            print('%s[-]bbands   : Failed%s '%(fg(9),attr(0)))
            return False

    '''
    !DO NOT TOUCH THE MA CODE, ALREADY COMPLETE.
    '''
    # Need to check the trend if its up or down for ema20,50,100.
    # v2 i using ema 20.
    def get_ema20_check_buy(self):
        endpoint = "https://api.taapi.io/ema"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'optInTimePeriod':20}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result   = json.loads(response.text)
        except:
            return 0
        return result["value"]


    def get_sma50_check_buy(self):
        endpoint = "https://api.taapi.io/sma"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'optInTimePeriod':50}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result   = json.loads(response.text)
        except:
            return 0
        return result["value"]

    def get_sma100_check_buy(self):
        endpoint = "https://api.taapi.io/sma"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'optInTimePeriod':100}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result   = json.loads(response.text)
        except:
            return 0
        return result["value"]

    '''
    !DO NOT TOUCH THE CODE, ALREADY COMPLETE.

    rsi is set to previous 3 candle (backtrack) to get optimise with candle pattern.
    - remove the comment to enable value display.
    '''
    def get_rsi_check_buy_uptrend(self):
        endpoint = "https://api.taapi.io/rsi"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'backtrack':3}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result   = json.loads(response.text)
        except:
            return False
        if(result["value"] > 80):
            #print('%s[-]RSI  %s:Failed%s ' %(fg(9),round(result["value"],6),attr(0)))
            print('%s[-]RSI up   : Failed%s ' %(fg(9),attr(0)))
            return False
        elif(result["value"] <= 35):
            #print('%s[+]RSI  %s:Success%s' %(fg(10),round(result["value"],6),attr(0)))
            print('%s[+]RSI up   : Success%s' %(fg(10),attr(0)))
            return True
        else:
            #print('%s[=]RSI  %s:Normal%s ' %(fg(142),round(result["value"],6),attr(0)))
            print('%s[=]RSI up   : Normal%s ' %(fg(142),attr(0)))
            return False

    '''
    ! DO NOT TOUCH THE CODE, ALREADY COMPLETE.
    '''
    def get_rsi_check_buy_downtrend(self):
        endpoint = "https://api.taapi.io/rsi"
        parameters = {'secret':api_taapi,'exchange':exchange,'symbol':self.symbol_taapi,'interval':interval,'backtrack':3}
        try:
            response = requests.get(url=endpoint,params = parameters)
            result   = json.loads(response.text)
        except:
            return False
        if(result["value"] > 80):
            #print('%s[-]RSI  %s:Failed%s ' %(fg(9),round(result["value"],6),attr(0)))
            print('%s[-]RSI down : Failed%s ' %(fg(9),attr(0)))
            return False
        elif(result["value"] <= 25):
            #print('%s[+]RSI  %s:Success%s' %(fg(10),round(result["value"],6),attr(0)))
            print('%s[+]RSI down : Success%s' %(fg(10),attr(0)))
            return True
        else:
            #print('%s[=]RSI  %s:Normal%s ' %(fg(142),round(result["value"],6),attr(0)))
            print('%s[=]RSI down : Normal%s ' %(fg(142),attr(0)))
            return False


    #--------------------------------------------------------------- buying mechanism --------------------------------------------------
    #--------------------------------------------------------------- selling mechanism -------------------------------------------------

    # do not set yet.

    #--------------------------------------------------------------- selling mechanism -------------------------------------------------

    #--------------------------------------------------------------- main function -----------------------------------------------------

'''
!DO NOT TOUCH THE CODE, ALREADY COMPLETE.
'''
#define argparse
parser = argparse.ArgumentParser()
parser.add_argument('symbol',nargs='+',help='place pair symbol e.g btc/usdt .')
parser.add_argument('usdt',nargs='+',type=float,help='usdt amount you want to trade.')
parser.add_argument('--execute',help='run a test for bot.')
parser.add_argument('--repeate',help='keep it running.')
args = parser.parse_args()

#input checking
if(args.usdt[0] <= 10):
    print("usdt price must be higher than 10$.")
    exit()

#main function
results = crypto_currency(args.symbol[0],args.usdt[0])
def main():
    print('--------------------------------')
    results.overall_results()
    results.pull_user_data()
    results.define_buy()
    results.bot_buy_check()
    results.bot_sell_check()
    print('--------------------------------')

#loop case
while(args.repeate == 'true'):
    try:
        main()
    except Exception as e:
        print(e)
    time.sleep(sleep_timer)

#non-loop
if(args.repeate == None):
    main()

    #--------------------------------------------------------------- main function -----------------------------------------------------
