import alpacaConfig as config 
import sqlite3
import pandas as pd 
pd.options.mode.chained_assignment = None  # default='warn'
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta, date
from patterns import patterns
import sys, os
import tulipy 
import numpy
import talib
# from collections import defaultdict #https://stackoverflow.com/questions/48136359/nested-lists-combine-values-according-to-first-value
# from itertools import groupby
from helpers import calculate_avg_volume20, calculate_vwap20, calculate_quantity, timeInterval, daysAwayMultiple
from timezone import is_dst #Checks if it's daylight savings
import matplotlib.pyplot as plt
import traceback
import bisect #For inserting into a sorted list



# This is for plotting trendlines
# import quandl as qdl
# from scipy.stats import linregress


import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning) #Ignore deprication warnings


#For support/resistance levels
import yfinance
import matplotlib.dates as mpl_dates



#NOTE: This script may take a lot of time to execute
# from momentumScreenForStocks import finalWatchlist #Import the final daily stock gainers with good volume, shares, and easy to borrow, and not a penny stock
# warnings.filterwarnings("ignore", category=DeprecationWarning) 

import smtplib, ssl
context = ssl.create_default_context() #Default context for emails


#Risk reward ratio
#SOME INPUTS: others are in the helpers script
###############################################################
risk = 1
reward = 1.5
pdtRule = 3 #Amount of trades before we cant daytrade (buy & sell on same day, normally 3)
actuallyTrade = True #If we should actually trade
shouldBacktest = False #True/False depending on if we need past data to backtest
trendingAboveEmaMonthlyPercentage = 0.60 #This X percentage above ema200 over the last month
tooBigAMove = 15 #EH's last candle was 19.374796 percent, but HUYA did really well and had a percent of 11.191047, so we'll do 15%

###############################################################


#CalculatedVars
###################################################
closeSlope = 0.000947515 #0.06947515   -> the MINIMUM LINEAR slope of the close price
# barsInPast = int(390/timeInterval) #Bars in a complete day within intraday
barsInPast = 1 #Daily
daysInPastGT = barsInPast*30 #30 days is enough to tell a general trend for swingin general trend

# candlesInPastForSlope = 6 #Taking the slope of 6 candles in the past for the linear slope

###################################################


macdAtrDict = {} #time, symbol for macd signal, atr value at the time



#IMPORTANT: 5 min timebars










#THIS BACKTEST IS STRAIGHT GREAT N ACCURATE. Change the other ema5/base all ur new backtesting data from this file (put GODDAM BLOOD INTO MAKING THIS IM GONNA FAINT)




        






conn = sqlite3.connect(config.dbFile) #connect to the database
conn.row_factory = sqlite3.Row #Make data indexable objects
cursor = conn.cursor() #Be able to write to the database

#get every categories info from the stock table
#RUN insertTrendingFibvizStocks2.py FIRST
# cursor.execute("""
#     SELECT * FROM stock 
# """)

if shouldBacktest:
    cursor.execute("""
        SELECT * from stock
    """)
else:
    cursor.execute("""
        SELECT * from stockGainers
    """)



stocks = cursor.fetchall() #fetch that stock table info from the cursor

stock_ids = {} #Initialize an empty dictionary
symbols = [] #start symbols list


# Add a couple of good stocks here to always look at
symbolsExtend = ['FLGT', 'API']

for symbol in symbolsExtend:
    if symbol not in symbols:
        symbols.append(symbol) #Append the symbol if not in the list



# symbolsToUse is an updated stock list of current uptrending stocks from https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change
symbolsToUse = ['TDC', 'BILL', 'MGNI', 'YALA', 'FLGT', 'GME', 'COLM', 'YSG', 'DNMR', 'DM', 'HTHT', 'SGEN', 'APPS', 'BEAM', 'CCIV', 'SKLZ', 'TGTX', 'OZON', 'SYNA', 'ATVI']
symbolsToUse.extend(symbolsExtend)
for stock in stocks:
    if shouldBacktest:
        if stock['symbol'] in symbolsToUse:
            symbol = stock['symbol'] #get the symbol index from stock
            # symbols.append(symbol)
            stock_ids[symbol] = stock['id'] #Make referencing the symbol return the id
            symbols.append(stock['symbol'])
    else:
        symbols.append(stock['symbol']) #Means we're actually trading and not assigning an ID to the stocks within the database
# print(symbols)
# sys.exit(1)

# sys.exit(1)
api = tradeapi.REST(config.apiKey, config.secretKey, base_url=config.baseUrl) #initialize the api

























# symbols = ['AAPL']
# print(symbols)
# sys.exit(1)



# symbols = ['API']
# symbols = symbols[:10] #Script kinda slow manually checking for ematrends, so just use first 10 symbols especially on the 5min

#Add a permanent watchlist on these symbols





# print(symbols)
# sys.exit(1)
"""
#https://trendarchitect.com/blog/how-to-calculate-the-exponential-moving-average
#Ema takes exactly ALL historical data in the past (check link above)
past_200ema_date = current_date - timedelta(days=200)

#Note: EMA just takes past 200 data within thinkorswim and that seems to work the best anyways. Take past 200 data, calculate EMA from that, BUT only access EMA within the market's range

numDaysBackNotWeekend = 204 #For some reason this results in 200 days but it's fine
while numDaysBackNotWeekend > 0:
    past_200ema_date -= timedelta(days=1) #Always go a day back
    if past_200ema_date.weekday() < 5: #But if it's not the weekend
        numDaysBackNotWeekend -= 1 #Count it as a day back
    else:
        pass #Otherwise just skip it (this else is just added for logic purposes but really isn't needed)
"""
######################## WE'RE GOING TO START 4 WEEKS BACK ON A MONDAY
numWeeksBack = 4
numDaysBack = 0 #How many days into the past do you want to go? (0 here)
messages = []



avgVolume = []

#rsi_period = 14


current_date = date.today()


justPrintInd = 0



# while start_date.weekday() != 0: #0 stands for monday. If it's not monday, just keep going back days
#     start_date -= timedelta(days=1) #This confirms that start_date is a monday


#Essentially go 4 weeks ahead and make sure it's a friday
end_date_range = current_date 




justPrintInt = 0

#This will take the pattern list, and combine it with each other accordingly since patterns just be different styles of the same thing
def patternPriceAction(listOfPatterns, data_market_hours):
    dojiDict = {}
    for pattern in listOfPatterns:
        p = getattr(talib, pattern) #make the string a talib function call
        dojiDict[pattern] = p(data_market_hours['open'], data_market_hours['high'], data_market_hours['low'], data_market_hours['close']) #open, high, low, close

    finalCombinedPattern = [0 for i in range(len(data_market_hours['open']))]
    for pattern in dojiDict:
        i = 0 #reset i for every individual item in the list of lists
        for val in dojiDict[pattern]:
            # print(val)
            if val != 0:
                finalCombinedPattern[i] = val #If we find any sort of pattern at this spot, we just assign it to that timeframe
            i += 1
    return finalCombinedPattern

#For support and resistance
def isSupport(df,i):
    support = df['low'][i] < df['low'][i-1]  and df['low'][i] < df['low'][i+1] and df['low'][i+1] < df['low'][i+2] and df['low'][i-1] < df['low'][i-2]
    return support
def isResistance(df,i):
    resistance = df['high'][i] > df['high'][i-1]  and df['high'][i] > df['high'][i+1] and df['high'][i+1] > df['high'][i+2] and df['high'][i-1] > df['high'][i-2]
    return resistance

#Make close support/resistance levels not even appear since it'll flood
def isFarFromLevel(l, levels, df):
    s =  numpy.mean(df['high'] - df['low']) #s is just some distance away from the high and low (the mean)
    return numpy.sum([abs(l-x) < s  for x in levels]) == 0


def getSupportResistance(symbol, data):
    name = symbol
    levels = []
    ticker = yfinance.Ticker(name)
    df = ticker.history(interval="1d",start="2020-11-11", end="2020-12-27")


    if is_dst():
        start_bar = f"{iteratorDate} 09:30:00-05:00"
        end_bar = f"{iteratorDate} 16:00:00-05:00"
    else:
        start_bar = f"{iteratorDate} 09:30:00-04:00"
        end_bar = f"{iteratorDate} 16:00:00-04:00"





    # fifteenMin = api.polygon.historic_agg_v2("SPY", 5, 'minute', _from=iteratorDate - timedelta(days=3), to=iteratorDate).df
    # # fifteenMin = fifteenMin.rename(columns={"open":"open", "close":"close", "high":"high", "low":"low", "volume":"volume"})
    # fifteenMin = fifteenMin.drop(columns="vwap", axis=0)


    # fifteenMin = fifteenMin.resample('15min').ffill()
    # fifteenMin_mask = (fifteenMin.index >= start_bar) & (fifteenMin.index < end_bar)
    # fifteenMin_bars = fifteenMin.loc[fifteenMin_mask]
    # print(fifteenMin)

    df = data
    # plt.plot(df['close'])
    # plt.show()
    # sys.exit(1)




    df['Date'] = pd.to_datetime(df.index)
    df['Date'] = df['Date'].apply(mpl_dates.date2num)
    df = df.loc[:,['Date', 'open', 'high', 'low', 'close']]

    



    # print(df.shape[0]-2) #The index of how many days are in the list - 2
    #Append each level
    # for i in range(2,df.shape[0]-2):
    #     if isSupport(df,i):
    #         levels.append((i,df['low'][i]))
    #     elif isResistance(df,i):
    #         levels.append((i,df['high'][i]))

    #Append supprot/resistance that's far from each other
    for i in range(2,df.shape[0]-2):
        if isSupport(df,i):
            l = df['low'][i]
            if isFarFromLevel(l, levels, df): #l is low
                levels.append((i,l))
        elif isResistance(df,i):
            l = df['high'][i]
            if isFarFromLevel(l, levels, df):
                levels.append((i,l))


    return levels


#Plot the levels
def plot_all(df, levels):
  fig, ax = plt.subplots()
  # candlestick_ohlc(ax,df.values,width=0.6, \
  #                  colorup='green', colordown='red', alpha=0.8)
  date_format = mpl_dates.DateFormatter('%d %b %Y')
  ax.xaxis.set_major_formatter(date_format)
  plt.plot(df['close'])
  fig.autofmt_xdate()
  # fig.tight_layout()
  for level in levels:
    plt.hlines(level[1],xmin=df['Date'][level[0]],\
               xmax=max(df['Date']),colors='blue')
  fig.show()



#Daily data
def stackData(inputDf, iteratorDate):
    frequency = '1D' #1D = 1 day, 1W = 1 week, 1M = 1 month
    #  5T 5minutes, 15T 15 minutes


    data = api.polygon.historic_agg_v2(symbol, 5, 'minute', _from=iteratorDate-timedelta(days=daysDist), to=iteratorDate).df #Get the data from that start_date to the end_date for the 5min bar date
    print(f"=== {symbol} Fetching from {(iteratorDate-timedelta(days=daysDist))} to {iteratorDate} with {frequency} bars")
    data_mask = []
    import datetime
    for dat in data.index:
        data_mask.append(dat.time() >= datetime.time(9,30,0) and dat.time() < datetime.time(16,0,0)) #Only get market hours
    data_market = data.loc[data_mask]
    # data_market = data



    
    #Resample it to dayily time
    data_market = data_market.resample(frequency, closed='right', label='right').agg(
        {'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
        }
    )



    # # #CHANGE THE ACTUAL TIME IN THE INDEXES
    for dat in range(len(data_market.index)):
        #dat.date() -= timedelta(days=1) #When we resample it, it pushes the day 1 up incorrectly
        datReplaceTime = data_market.index[dat].replace(hour=15, minute=45) #Just a time we want to trade at (this isn't really necessary)
        datReplaceTime -= timedelta(days=1) #It's pushing the days up by 1
        data_market.index.values[dat] = datReplaceTime #Replace the time at the index with the time we want to trade at
        #print(dat) #Doesn't include weekends/holidays
        pass

    #There's repeat indexes with the same damn info. Removing them https://stackoverflow.com/questions/13035764/remove-pandas-rows-with-duplicate-indices
    data_market = data_market[~data_market.duplicated(keep='first')]
    



    #iteratorDate += timedelta(days=daysDist) #Just add the days distance to it

    

    




    

    #https://stackoverflow.com/questions/29351840/stack-two-pandas-data-frames
    inputDf = pd.concat([inputDf, data_market])
    return inputDf






#time -> 1,2,3,4,5...
#frequency -> 'hour', 'day', 'minute'
def stackDataIntraday(inputDf, iteratorDate, time, frequency):
    #Just copy paste the above code from under date (this isn't a function sorry mate)
    data = api.polygon.historic_agg_v2(symbol, time, frequency, _from=iteratorDate-timedelta(days=daysDist), to=iteratorDate).df #Get the data from that start_date to the end_date for the 5min bar date
    print(f"=== {symbol} Fetching from {(iteratorDate-timedelta(days=daysDist))} to {iteratorDate} with {timeInterval}min bars")
    data_mask = []
    import datetime
    for dat in data.index:
        data_mask.append(dat.time() >= datetime.time(9,30,0) and dat.time() < datetime.time(16,0,0)) #Only get market hours
    data_market = data.loc[data_mask]



    
    #Resample it to dayily time
    # data_market = data_market.resample('1D', closed='right', label='right').agg(
    #     {'open': 'first',
    #     'high': 'max',
    #     'low': 'min',
    #     'close': 'last',
    #     'volume': 'sum'
    #     }
    # )



    # # #CHANGE THE ACTUAL TIME IN THE INDEXES
    # for dat in range(len(data_market.index)):
    #     #dat.date() -= timedelta(days=1) #When we resample it, it pushes the day 1 up incorrectly
    #     datReplaceTime = data_market.index[dat].replace(hour=15, minute=45)
    #     datReplaceTime -= timedelta(days=1)
    #     data_market.index.values[dat] = datReplaceTime #Replace the time at the index with the time we want to trade at
    #     #print(dat) #Doesn't include weekends/holidays
    



    #iteratorDate += timedelta(days=daysDist) #Just add the days distance to it

    

    




    

    #https://stackoverflow.com/questions/29351840/stack-two-pandas-data-frames
    inputDf = pd.concat([inputDf, data_market])
    return inputDf


def buyOrSellStock(symbol, buyOrSell, take_profit, stop_loss, actuallyTrade):
    if actuallyTrade == False:
        return #Just dont trade if it's false

    if len(allMarketOrders) < pdtRule:
        try:
            # stop_loss = data_market_hours['close'][-1] - (data_market_hours['atr'][-1] * risk) #Using atr and a multiple away from it (risk) to get the stoploss
            # take_profit = data_market_hours['close'][-1] + (data_market_hours['atr'][-1] * reward) #This is the method for a risk:reward ratio
            
            #Setting the minimum val here (needed sometimes)
            if abs(take_profit - data_market_hours['close'][-1]) < 0.1 or abs(data_market_hours['close'][-1] - stop_loss) < 0.1:
                # print(take_profit)
                take_profit += 0.9 #If it doesn't fit the criteria of the buy (0.01 more than close), just spread the take_profit and stop_loss more
                stop_loss -= 0.9
                print("Had to spread take_profit")
            # print(f"Stoploss: {stop_loss} Close {data_market_hours['close'][-1]} Profit {take_profit}")

            api.submit_order(
                symbol=symbol,  
                side=buyOrSell, #buy or sell
                type='market', #Just going to ensure the buying price for the quantity so there's no issues with balance
                qty=1,  #int(calculate_quantity(data_market_hours.close.values[-1])),  #We're going to use 95% of our bp for every purchase (check the function for clarification)
                time_in_force='day',
                order_class='bracket',
                stop_loss={'stop_price': stop_loss},
                take_profit={'limit_price': take_profit}
            )
            print(f"{buyOrSell} executed")
        except Exception as e:
            print(f"Couldnt buy {e}")

def closeOrders(symbol, side, qty):
    if side == 'long':
        side = 'sell' #Opposite side to correctly buy/sell to liquidate
    elif side == 'short':
        side = buy
    
    api.submit_order(
        symbol=symbol,  
        side=side, #buy or sell
        type='market', #Just going to ensure the buying price for the quantity so there's no issues with balance
        qty=qty,  #int(calculate_quantity(data_market_hours.close.values[-1])),  #We're going to use 95% of our bp for every purchase (check the function for clarification)
        time_in_force='day'

    )

            






startTime = "15:45:00"
endTime = "15:45:00"

takeOneDailyTime = "15:45:00" #This is 3:45. We'll trade during this timeperiod





if shouldBacktest:
    daysDist = 20 #3 is a good number. For backtesting, bump it up to 20
else:
    daysDist = 3

iteratorDate = current_date-timedelta(days=daysDist*daysAwayMultiple) #daysDist*18 is a time effective past history (we only need 200 days in the past)
iterCopy = iteratorDate #For when we are resetting the symbols

allPositions = api.list_positions()
existing_order_symbols = [order.symbol for order in allPositions]
allOrdersFull = [order for order in allPositions]


allMarketOrders = api.list_orders(status='all', after=current_date)
allMarketOrders = [order for order in allMarketOrders if order.type=='market' and order.status != 'canceled'] #This is only market orders, so just get all the orders we did today (this should be less than 3 to do an order for daytrading)




# symbols = ['BDX', 'KMI', 'RIOT', 'NIO', 'EBAY', 'ODFL', ''] #, 'BDX', 'ODFL', 'NKE', 'EBAY'
# symbols.extend(['TSLA', 'AMZN', 'RIOT', 'NIO', 'FB', 'TWTR', 'SNAP', 'AAPL', 'MSFT', 'GOOG', 'W'])

# import random 
# symbols = random.sample(symbols, 30) #Select 30 distinct items in the list https://stackoverflow.com/questions/306400/how-to-randomly-select-an-item-from-a-list
# symbols = ['GME', 'BBBY', 'CCIV', 'SPCE', 'BB']
# print(symbols)
# sys.exit(1)



# finalWatchlist = ['PLTR', 'AAPL']#These stocks should up/downtrend
# finalWatchlist = ['CCIV', 'AAPL']
# finalWatchlist = ['RCON', 'AMTX', 'TSIA', 'AMC', 'ADMP', 'GME', 'AZRX', 'CCIV', 'BB', 'AAPL', 'BAC', 'MARA', 'FCEL', 'QTT', 'RLX', 'OPTT', 'IDEX', 'IBM', 'BBBY', 'HBAN', 'PBR', 'RIG', 'FUBO', 'ZNGA', 'OGEN', 'ABEV', 'T', 'BIOL', 'ITUB', 'TNXP', 'ATOS', 'CLII', 'OPTT', 'EXPR', 'GSAT', 'RCON', 'GIGM']




# finalWatchlist = ['SPY', 'GME', 'PLUG', 'CCL', 'MSFT', 'BYND', 'ATOS']
# # finalWatchlist = ['BYND']
# symbols = finalWatchlist #Just set this equal to this list of stocks (day gainers)


# #SIMMMMPLY make sure that we have symbols in the order already
# for symbol in existing_order_symbols:
#     if symbol not in symbols:
#         symbols.append(symbol)


# ['GME', 'VIR', 'BZUN', 'BLNK', 'WKHS', 'NNOX', 'OSTK', 'BBBY', 'FCEL', 'DDS', 'YQ', 'BYND', 'SPCE', 'API', 'STAA', 'FIZZ', 'APPN', 'RIDE', 'SPWR', 'MAC']
# symbols = symbols[:8] #Only get first 10 symbols (20 in total, but it's laggy)
# symbols = ['AAPL', 'TSLA', 'GME', 'BBBY', 'API', 'FIZZ', 'AAPN']
# symbols = ['API', 'AAPL', 'FLGT', 'AMC', 'BBBY', 'WISH', 'BNTX', 'VIR']
# symbols = ['FUTU', 'TLRY', 'CCIV', 'AI', 'GRWG', 'DQ', 'KC', 'OPEN', 'NTLA', 'WDAY', 'SPR', 'UBER', 'FTCH', 'PENN', 'BILI', 'AAPL', 'AMC', 'RIOT']
# import ctypes  # An included library with Python install.   
# ctypes.windll.user32.MessageBoxW(0, "Your text", "Your title", 1)
# symbols = ['GME']
# symbols = ['API', 'AAPL', 'FLGT', 'AMC', 'BBBY', 'WISH', 'BNTX', 'VIR']

# symbols = symbolsToUse

# symbols = ['AA', 'AAOI', 'ABEQ', 'ACIO', 'ACV', 'ACST', 'ACWI', 'AES', 'AEMD', 'ADUS', 'AHH', 'AIR']
symbols = ['IRM']

for order in allOrdersFull:
    #Closes all positions (really dont need to pass anything but the order object in here, but it's fine)
    closeOrders(order.symbol, order.side, order.qty)



messages.append('Closed Orders For the day')
with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD) #Login
    email_message = f"Subject: Closed Positions: {current_date}\n\n" #Our email subject

    email_message += "\n\n".join(messages) #Our message
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message) #From, to, message (sending to ourself)
    print("End execution")

    
    


