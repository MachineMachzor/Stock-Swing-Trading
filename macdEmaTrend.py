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
tooBigAMove = 15 #EH's last candle was 19.374796 percent, but HUYA did really well and had a percent of 11.191047, so we'll do 15% (just brainless thinking amirite?)

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
# symbolsToUse = ['TDC', 'BILL', 'MGNI', 'YALA', 'FLGT', 'GME', 'COLM', 'YSG', 'DNMR', 'DM', 'HTHT', 'SGEN', 'APPS', 'BEAM', 'CCIV', 'SKLZ', 'TGTX', 'OZON', 'SYNA', 'ATVI']
# symbolsToUse = ['BYND', 'MVIS', 'YALA', 'AMKR', 'HUYA', 'RIOT', 'Z', 'ZG', 'SONO', 'GNRC', 'SPCE', 'OSH', 'PACB', 'MARA', 'TPX', 'KLAC', 'AXON', 'LRCX', 'FVRR', 'PINS', 'MGNI', 'HTHT', 'EXPI', 'UPWK', 'OSTK', 'AMAT', 'OPCH', 'LAZR', 'RDFN', 'KLIC', 'MXL', 'CD', 'WDC', 'HZNP', 'OPEN', 'IIVI', 'NIU', 'CALX', 'RUN', 'FRHC', 'CDAY', 'MU', 'TER', 'TENB', 'API', 'IQ', 'AZEK', 'STM', 'FTCH', 'UPST', 'SKY', 'VSTO', 'REAL', 'CDNS', 'YY', 'RIDE', 'FAF', 'TSM', 'PSTG', 'MXIM', 'MCHP', 'SMAR', 'CREE', 'GH', 'QRVO', 'LTHM', 'BAM', 'SI', 'MSTR', 'ADI', 'ENTG', 'LH', 'LMND', 'VRNS', 'BLDP', 'SKX', 'JKS', 'ST', 'CBRE', 'NVDA', 'SQ', 'NXPI', 'CTLT', 'YELP', 'MRVL', 'TCOM', 'LSPD', 'GSX', 'MPWR', 'INTU', 'SAIL', 'SPG', 'BNGO', 'TXN', 'STNE', 'APTV', 'URBN', 'BEKE', 'TXT', 'CINF', 'MA', 'TMHC', 'WB', 'KBH', 'CC', 'PPD', 'ABNB', 'ALB', 'BYND', 'ZTS', 'ZTO', 'WELL', 'OLN', 'MRNA', 'VTR', 'FMC', 'REG', 'NVST', 'TWOU', 'STX', 'YUMC', 'BG', 'DAR', 'AHCO', 'EW', 'TME', 'ACGL', 'SPGI', 'CRM', 'TMO', 'EL', 'EA', 'GRUB', 'SWKS', 'INFO', 'UNP', 'BIDU', 'HIW', 'FL', 'THC', 'BHC', 'AVGO', 'DDOG', 'LYV', 'CHWY', 'TT', 'BLDR', 'YNDX', 'SIG', 'RCM', 'SPWR', 'HAIN', 'LAC', 'JCI', 'NTNX', 'W', 'ONEM', 'LI', 'LYFT', 'GOOS', 'A', 'CRWD', 'HWM', 'CAKE', 'IQV', 'ETN', 'MD', 'SE', 'DHR', 'ROST', 'IRBT', 'ON', 'NNN', 'CHGG', 'ABT', 'GDDY', 'CTSH', 'DGX', 'TOL', 'ZBH', 'TWTR']
symbolsToUse = ['BEKE', 'CRWD', 'EH', 'GEVO', 'HUYA', 'IQV', 'IRM', 'JD', 'PACB', "SYF", 'BBL']
# symbolsToUse.extend(symbolsExtend)
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
            qty=2,  #int(calculate_quantity(data_market_hours.close.values[-1])),  #We're going to use 95% of our bp for every purchase (check the function for clarification)
            time_in_force='gtc',
            order_class='bracket',
            stop_loss={'stop_price': stop_loss},
            take_profit={'limit_price': take_profit}
        )
        print(f"{buyOrSell} executed")
    except Exception as e:
        print(f"Couldnt buy {e}")
            






startTime = "15:45:00"
endTime = "15:45:00"

takeOneDailyTime = "15:45:00" #This is 3:45. We'll trade during this timeperiod





# if shouldBacktest:
#     daysDist = 20 #3 is a good number. For backtesting, bump it up to 20
# else:
#     daysDist = 3

daysDist = 3 #We dont gotta go far to backtest. Only doing 1d at a time

iteratorDate = current_date-timedelta(days=daysDist*daysAwayMultiple) #daysDist*18 is a time effective past history (we only need 200 days in the past)
iterCopy = iteratorDate #For when we are resetting the symbols

allPositions = api.list_positions()
existing_order_symbols = [order.symbol for order in allPositions]


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
# symbols = ['IRM']

for symbol in symbols:
    #CLB, TSLA, UAA
    data_market_hours = pd.DataFrame() #Reset the data for each symbol
    data_market_hours_trend = pd.DataFrame() #For our ematrend
    levels = [] #reset the levels for each new timeframe

    while iteratorDate < current_date:
        #Backtesting range. Starting from today go like 45 days back -> we're just going to call the api for everyday within the normal range
        #start_date = date.today()
        #end_date_range = start_date - timedelta(days=45)
        #Going to backtest 4 weeks back on Monday
        

        # print(f"{iteratorDate} #####") #Go lookup both of these dates if you come back and ur unsure


        # data = api.polygon.historic_agg_v2(symbol, timeInterval, 'minute', _from=iteratorDate-timedelta(days=daysDist), to=iteratorDate).df #Get the data from that start_date to the end_date for the 5min bar date
        # print(f"=== {symbol} Fetching from {(iteratorDate-timedelta(days=daysDist))} to {iteratorDate} with {timeInterval}min bars")
        # # data = data.resample(f'{timeInterval}T').ffill() #Forward fill missing timeframe datapoints -> this actually fills in weekends, so we don't do this
        # data_mask = []
        # import datetime
        # for dat in data.index:
        #     data_mask.append(dat.time() >= datetime.time(9,30,0) and dat.time() < datetime.time(16,0,0)) #Only get market hours
        # data_market = data.loc[data_mask]



        
        #Resample it to dayily time
        # data_market = data_market.resample('1D', closed='right', label='right').agg(
        #     {'open': 'first',
        #     'high': 'max',
        #     'low': 'min',
        #     'close': 'last',
        #     'volume': 'sum'
        #     }
        # )


        # #CHANGE THE ACTUAL TIME IN THE INDEXES
        # for dat in range(len(data_market.index)):
        #     #dat.date() -= timedelta(days=1) #When we resample it, it pushes the day 1 up incorrectly
        #     datReplaceTime = data_market.index[dat].replace(hour=15, minute=45)
        #     datReplaceTime -= timedelta(days=1)
        #     data_market.index.values[dat] = datReplaceTime #Replace the time at the index with the time we want to trade at
        #     #print(dat) #Doesn't include weekends/holidays
        



        #iteratorDate += timedelta(days=daysDist) #Just add the days distance to it

        

        



        """
        timespan is the size of the time window, can be one of [minute, hour, day, week, month, quarter, year]
        """



        """
        Aggs entity. multiplier is the size of the timespan multiplier. timespan is the size of the time window, can be one of minute, hour, day, week, month, quarter or year. _from and to must be in YYYY-MM-DD format, e.g. 2020-01-15.
        """

        #Note: Extend the amount of days here to reflect the period. Also note, days=73 doesn't mean 73 days. Do print(len(data)) and extend the days here to incorporate however many days u want
        # data = api.polygon.historic_agg_v2(symbol, timeInterval, 'minutes', _from=iteratorDate-timedelta(days=14), to=iteratorDate).df #Get the data from that start_date to the end_date for the 5min bar date

        

        #https://stackoverflow.com/questions/29351840/stack-two-pandas-data-frames
        # data_market_hours = pd.concat([data_market_hours, data_market])
        # data_market_hours = stackDataIntraday(data_market_hours, iteratorDate, timeInterval, 'minute') #normal trading timeframe (15min)
        # data_market_hours = stackDataIntraday(data_market_hours, iteratorDate, 30, 'minute') #trend trading timeframe (30min)

        # data_market_hours_long = stackDataIntraday(data_market_hours_long, iteratorDate, 4, 'hour') #4hr data
        data_market_hours = stackData(data_market_hours, iteratorDate) #daily data



        # print(data_market)
        # print(daily_market)
  
        # 

        # print(len(data))
        # 
        
        remainingCopy = iteratorDate #Before we update iteratorDate to potentially stop the loop, we set it equal to this variable so we can add the remaining data
        iteratorDate += timedelta(days=daysDist) #Just add the days distance to it

    #Get the remaining data
    if remainingCopy < iteratorDate:
        #Just copy paste the above code from under date (this isn't a function sorry mate)
        # data = api.polygon.historic_agg_v2(symbol, timeInterval, 'minute', _from=remainingCopy, to=iteratorDate).df #Get the data from that start_date to the end_date for the 5min bar date
        # print(f"=== {symbol} Fetching from {(iteratorDate-timedelta(days=daysDist))} to {iteratorDate} with {timeInterval}min bars")
        # data_mask = []
        # import datetime

        # for dat in data.index:
        #     data_mask.append(dat.time() >= datetime.time(9,30,0) and dat.time() < datetime.time(16,0,0)) #Only get market hours
        # data_market = data.loc[data_mask]





        
        #Resample it to dayily time
        # data_market = data_market.resample('1D', closed='right', label='right').agg(
        #     {'open': 'first',
        #     'high': 'max',
        #     'low': 'min',
        #     'close': 'last',
        #     'volume': 'sum'
        #     }
        # )



        # #CHANGE THE ACTUAL TIME IN THE INDEXES
        # for dat in range(len(data_market.index)):
        #     #dat.date() -= timedelta(days=1) #When we resample it, it pushes the day 1 up incorrectly
        #     datReplaceTime = data_market.index[dat].replace(hour=15, minute=45)
        #     datReplaceTime -= timedelta(days=1)
        #     data_market.index.values[dat] = datReplaceTime #Replace the time at the index with the time we want to trade at
        #     #print(dat) #Doesn't include weekends/holidays
        



        #iteratorDate += timedelta(days=daysDist) #Just add the days distance to it

        

        



        """
        timespan is the size of the time window, can be one of [minute, hour, day, week, month, quarter, year]
        """



        """
        Aggs entity. multiplier is the size of the timespan multiplier. timespan is the size of the time window, can be one of minute, hour, day, week, month, quarter or year. _from and to must be in YYYY-MM-DD format, e.g. 2020-01-15.
        """

        #Note: Extend the amount of days here to reflect the period. Also note, days=73 doesn't mean 73 days. Do print(len(data)) and extend the days here to incorporate however many days u want
        # data = api.polygon.historic_agg_v2(symbol, timeInterval, 'minutes', _from=iteratorDate-timedelta(days=14), to=iteratorDate).df #Get the data from that start_date to the end_date for the 5min bar date

        

        #https://stackoverflow.com/questions/29351840/stack-two-pandas-data-frames
        # data_market_hours = pd.concat([data_market_hours, data_market])
        # data_market_hours = stackDataIntraday(data_market_hours, iteratorDate, timeInterval, 'minute') #normal trading timeframe (15min)
        # data_market_hours = stackDataIntraday(data_market_hours, iteratorDate, 30, 'minute') #trend trading timeframe (30min)
        data_market_hours = stackData(data_market_hours, iteratorDate) #daily data




        # data_market_hours_long = stackDataIntraday(data_market_hours_long, iteratorDate, 4, 'hour') #4hr data
        # data_market_hours_longer = stackData(data_market_hours_longer, iteratorDate) #daily data




        



    else:
        print(iteratorDate) #Fixed this by setting iteratorDate to iterCopy AFTER this if statement in order to reset it to the original date, so this else shouldnt be hit
        print(remainingCopy)

    # levels.extend(getSupportResistance(symbol, data_market_hours)) #Get the support and resistance lines for however much prior we're going
    #There's repeat indexes with the same damn info. Removing them https://stackoverflow.com/questions/13035764/remove-pandas-rows-with-duplicate-indices
    data_market_hours = data_market_hours[~data_market_hours.duplicated(keep='first')]
    # print(len(data_market_hours))
    


    iteratorDate = iterCopy #Reset the date for the next symbol
    # plot_all(data_market_hours, levels)
    # plt.show()
    # sys.exit(1)

    # print(data_market_hours)
    # sys.exit(1)
    # print(data_market_hours)



    

    
    
    #NOW WE HAVE THE daily_market DATA, SO WE CAN NOW START TO USE IT
    data_market_hours = data_market_hours.dropna() #Just drop all rows with NaN values

    
    # data0 = data_market_hours.copy()
    # # print(data0.index.date())
    # # print(data0.index.date)
    # # print(data0.index.date.min())

    # # sys.exit(1)
    # # dates = []
    # # for dat in data0.index:
    # #     dates.append(((dat.date() - data0.index[0].date())))
    # # print(dates)
    # # sys.exit(1)
    # data0['date_id'] = ((data0.index.date - data0.index.date.min())).astype('timedelta64[D]')
    # data0['date_id'] = data0['date_id'].dt.days + 1

    # # for i, date in enumerate(dates):
    # #     dates[i] = date + timedelta(days=1)
    # # print(dates)
    # # sys.exit(1)
    # # print(data0)
    # # sys.exit(1)

    # # high trend line

    # data1 = data0.copy()

    # while len(data1)>3:

    #     reg = linregress(
    #                     x=data1['date_id'],
    #                     y=data1['high'],
    #                     )
    #     data1 = data1.loc[data1['high'] > reg[0] * data1['date_id'] + reg[1]]

    # reg = linregress(
    #                     x=data1['date_id'],
    #                     y=data1['high'],
    #                     )

    # data0['high_trend'] = reg[0] * data0['date_id'] + reg[1]

    # # low trend line

    # data1 = data0.copy()

    # while len(data1)>3:

    #     reg = linregress(
    #                     x=data1['date_id'],
    #                     y=data1['low'],
    #                     )
    #     data1 = data1.loc[data1['low'] < reg[0] * data1['date_id'] + reg[1]]

    # reg = linregress(
    #                     x=data1['date_id'],
    #                     y=data1['low'],
    #                     )

    # data0['low_trend'] = reg[0] * data0['date_id'] + reg[1]

    # # plot

    # data0['close'].plot()
    # data0['high_trend'].plot()
    # data0['low_trend'].plot()
    # plt.show()
    # sys.exit(1)

    

    # print(data_market_hours)
    # print(len(data_market_hours))
    # sys.exit(1)
    # 

    
    
    
    


        #if len(data.index) != 0: #If it actually generated data
        #Only get the market hours for this current bar
    if is_dst():
        start_bar = f"{iteratorDate} {startTime}-05:00" #The 05:00 is just for daylight savings in the US. Check for whatever state ur in
        end_bar = f"{iteratorDate} {endTime}-05:00" #Change this to test specific times
    else:
        start_bar = f"{iteratorDate} {startTime}-04:00" #Not daylight savings
        end_bar = f"{iteratorDate} {endTime}-04:00"





    #If there were market hours this day
    if len(data_market_hours) > 0:

        try:
            #Now, we're going to find the closest level BELOW the close and ABOVE the close, find which one is CLOSER, THEN see if the trade will head the OTHER WAY FROM the closest level since it's a support/resistance BOUNCE
            levels_valsOnly = []
            # #For every level
            for level in levels:
                levels_valsOnly.append(level[1]) #Only append support and resistance lines
            levels_valsOnly.sort() #Just order the support/resistance into an orderly fashion
            bisect.insort(levels_valsOnly, data_market_hours.close.values[-1]) #Insort (insert into a sorted list correctly) the last close price
            closeInd = levels_valsOnly.index(data_market_hours.close.values[-1]) #Find where it inserted the close price
            


           

            macDFastPeriod = 12 #8 12
            macDPeiod = 9 #5 9
            macDSlowPeriod = 26 #21 28

            # rsi = tulipy.rsi(data_market_hours['close'].values, rsiPeriod) #real, period
            #14 period

            #Real: .04     AtrVal: 0.057552067077396865
            # for i in range(rsiPeriod):
            #     rsi = numpy.insert(rsi, 0, None, axis=0) #For rsi, at index 0, insert None at axis=0 (x axis, horizontal)

            # for i in range(rsiPeriod-1):
            #     atr = numpy.insert(atr, 0, None, axis=0) #atr's period is 1 less than 14 for some reason

            #https://openwritings.net/pg/python-draw-macd-using-tulip-indicators-matplotlib (where I got the variable outputs, (macd, macd_signal) idea from) 
            macd, macd_signal, macd_histogram = tulipy.macd(data_market_hours['close'].values, macDFastPeriod, macDSlowPeriod, macDPeiod) #real, shortperiod, longperiod, signalperiod

            ema200 = tulipy.ema(data_market_hours['close'].values, 200)

            for i in range(abs(len(data_market_hours) - len(ema200))):
                ema200 = numpy.insert(ema200, 0, None, axis=0)

            data_market_hours['ema200'] = ema200


            


            # data_market_hours['avgVolume'] = data_market_hours['volume'].rolling(window=20).mean() #20 period avgVol
            




            

            emasSameDir = [None] #Checking 1 candle behind, so we do this
            posDir = 1
            negDir = -1
            neutral = 0

            #Adding ATR for TP (target profit) and SL (stoploss)
            atr = tulipy.atr(data_market_hours['high'].values, data_market_hours['low'].values, data_market_hours['close'].values, 14) #high, low, close, period
            for i in range(abs(len(atr) - len(data_market_hours))): #The difference in the length lists
                atr = numpy.insert(atr, 0, None, axis=0) #insert Nones in the front to make list the same length
            data_market_hours['atr'] = atr

            macdCrossing = tulipy.crossover(macd, macd_signal) #macd crossing the signal line
            # print(len(macdCrossing))
            # print(len(data_market_hours))


            for i in range(abs(len(data_market_hours)-len(macdCrossing))):
                macdCrossing = numpy.insert(macdCrossing, 0, None, axis=0) #Make lists same length

            for i in range(abs(len(data_market_hours)-len(macd_histogram))):
                macd_histogram = numpy.insert(macd_histogram, 0, None, axis=0) #Make lists same length


            data_market_hours['macdCrossing'] = macdCrossing
            crossBuySellMacd = []
            #Get exact buy/sell signals from macd crossings
            for i in range(len(data_market_hours)):
                if macdCrossing[i] == 1 and macd_histogram[i] > 0:
                    crossBuySellMacd.append(posDir)
                elif macdCrossing[i] == 1 and macd_histogram[i] < 0:
                    crossBuySellMacd.append(negDir)
                else:
                    crossBuySellMacd.append(neutral)
            data_market_hours['crossBuySellMacd'] = crossBuySellMacd
            
                
            

            # for i in range(len(data_market_hours)):
            #     print("{} {}".format(data_market_hours.index[i], data_market_hours.macdCrossing[i]))
            
     


            # sys.exit(1)



            # if shouldBacktest:
            #     # for i in range(1, len(data_market_hours)):
            #     #     pass
            #         #DEALING WITH emas GOING SAME DIRECTION
            #         #ema50 - previous ema50 is greater than 0 (going up) repeated for ema9 and 200. done to see if it's below 0 to see if negative trending
            #         # if (data_market_hours['ema50'][i] - data_market_hours['ema50'][i-1] > 0 and data_market_hours['ema9'][i] - data_market_hours['ema9'][i-1] > 0 and data_market_hours['ema200'][i] - data_market_hours['ema200'][i-1] > 0):
            #         #     emasSameDir.append(posDir) #All emas greater than their past candle
            #         # elif (data_market_hours['ema50'][i] - data_market_hours['ema50'][i-1] < 0 and data_market_hours['ema9'][i] - data_market_hours['ema9'][i-1] < 0 and data_market_hours['ema200'][i] - data_market_hours['ema200'][i-1] < 0):
            #         #     emasSameDir.append(negDir)
            #         # else:
            #         #     emasSameDir.append(neutral)

                


                    
            #     # emasGeneralTrend = [] #all emas moving in same direction CURRENTLY (using 1 candle back to get dir)
            #     # aboveAvgVolume = [] #if vol is above 20 period MA
            #     # candleBullOrBear = [] #Literally states if the candle is green or red
            #     # for i in range(len(data_market_hours)):
            #     #     # DEALING WITH CROSSOVER STUFF ON EMA50 AND EMA200 (just which crossover it's at rn, like ema50 > ema200 uptrend)
            #     #     if data_market_hours['ema9'][i] - data_market_hours['ema200'][i] > 0: #ema50 above
            #     #         emasGeneralTrend.append(posDir)
            #     #     elif data_market_hours['ema9'][i] - data_market_hours['ema200'][i] < 0:
            #     #         emasGeneralTrend.append(negDir)
            #     #     else:
            #     #         emasGeneralTrend.append(neutral) #They're the same (inconclusive)

            #     #     #DEALING WITH VOLUME
            #     #     if data_market_hours['volume'][i] > data_market_hours['avgVolume'][i]:
            #     #         aboveAvgVolume.append(posDir) #Positive can mean good for both up and downtrends since above avg volume means trend continuation
            #     #     elif data_market_hours['volume'][i] < data_market_hours['avgVolume'][i]:
            #     #         aboveAvgVolume.append(negDir)
            #     #     else:
            #     #         aboveAvgVolume.append(neutral) #avgVol and volume are equal somehow

            #     #     #DEALING WITH IF IT'S BULL OR BEAR CANDLE
            #     #     if data_market_hours['close'][i] - data_market_hours['open'][i] > 0: #closed above where it opened, so it increased
            #     #         candleBullOrBear.append(posDir)
            #     #     elif data_market_hours['close'][i] - data_market_hours['open'][i] < 0:
            #     #         candleBullOrBear.append(negDir)
            #     #     else:
            #     #         candleBullOrBear.append(neutral)

            #     generalSlope = []
            #     # print(len(data_market_hours))
            #     #Gets the slope for the last 30 days
            #     for i in range(len(data_market_hours)):
            #         if i >= daysInPastGT:
            #             generalSlope.append(tulipy.linregslope(data_market_hours['close'][i+1-daysInPastGT:i+1].values, daysInPastGT)[0])
            #         else:
            #             generalSlope.append(None)

            #     data_market_hours['generalSlope'] = generalSlope
            #     # print(linregslope)
            #     # sys.exit(1)
                    




            #     # data_market_hours['emasSameDir'] = emasSameDir #Focus this to use on entries since all emas are in the CURRENT same direction
            #     # data_market_hours['emasGeneralTrend'] = emasGeneralTrend  #this focuses on if the ema50 is ABOVE the ema200 OR NOT. This is more GENERAL
            #     # data_market_hours['aboveAvgVolume'] = aboveAvgVolume #if volume is above the avg volume
            #     # data_market_hours['candleBullOrBear'] = candleBullOrBear #identifies if it's a red or green candle (close > open, green)
            #     # print(data_market_hours)
            #     # print(data_market_hours)
            #     # sys.exit(1)

                
                

            #     # closeSlope = tulipy.linregslope(data_market_hours['close'][-16:].values, 16)

            #     # print(barsInPast)
                

            #     #Current trending above ema200 for today only
            #     trendingAboveEmaDay = [None for i in range(barsInPast)]
            #     for i in range(barsInPast, len(data_market_hours)):
            #         startingVal = i-barsInPast #This is like a moving box. We always want to check X bars back for every one bar
            #         aboveEma = 0
            #         belowEma = 0
            #         allChecks = 0
            #         # if data_market_hours['close'][i]
            #         for j in range(startingVal, i):
            #             if data_market_hours['close'][j] - data_market_hours['ema200'][j] > 0: #A close price above the ema200
            #                 aboveEma += 1
            #             elif data_market_hours['close'][j] - data_market_hours['ema200'][j] < 0:
            #                 belowEma += 1
            #             allChecks += 1 #Everytime we check a point

            #         #If it's 80% above the ema200
            #         if (aboveEma/allChecks) > 0.80:
            #             trendingAboveEmaDay.append(posDir)
            #         elif (belowEma/allChecks) > 0.80:
            #             trendingAboveEmaDay.append(negDir)
            #         else:
            #             trendingAboveEmaDay.append(neutral)
                
            #     data_market_hours['trendingAboveEma'] = trendingAboveEmaDay


            #     #If it was trending above/below ema200 for a month
            #     # trendingAboveEmaMonth = [None for i in range(daysInPastGT)]
            #     # for i in range(daysInPastGT, len(data_market_hours)):
            #     #     startingVal = i-daysInPastGT #This is like a moving box. We always want to check X bars back for every one bar
            #     #     aboveEma = 0
            #     #     belowEma = 0
            #     #     allChecks = 0
            #     #     # if data_market_hours['close'][i]
            #     #     for j in range(startingVal, i):
            #     #         if data_market_hours['close'][j] - data_market_hours['ema200'][j] > 0: #A close price above the ema200
            #     #             aboveEma += 1
            #     #         elif data_market_hours['close'][j] - data_market_hours['ema200'][j] < 0:
            #     #             belowEma += 1
            #     #         allChecks += 1 #Everytime we check a point

            #     #     #If it's 80% above the ema200
            #     #     if (aboveEma/allChecks) > trendingAboveEmaMonthlyPercentage:
            #     #         trendingAboveEmaMonth.append(posDir)
            #     #     elif (belowEma/allChecks) > trendingAboveEmaMonthlyPercentage:
            #     #         trendingAboveEmaMonth.append(negDir)
            #     #     else:
            #     #         trendingAboveEmaMonth.append(neutral)
                
            #     # data_market_hours['trendingAboveEmaMonth'] = trendingAboveEmaMonth

                


                

            #     # movingSlope = [None for i in range(candlesInPastForSlope)]
            #     # print(len(movingSlope))
            #     # sys.exit(1)
            #     # for i in range(candlesInPastForSlope, len(data_market_hours)):
            #     #     slope = tulipy.linregslope(data_market_hours['close'][i+1-candlesInPastForSlope:i+1].values, candlesInPastForSlope)[0]
            #     #     # print(f"{data_market_hours['close'][i+1-candlesInPastForSlope:i+1].values} \n\n\n") We add +1 so it includes the current candle
            #     #     movingSlope.append(slope)
            #     # data_market_hours['movingSlope'] = movingSlope
                
                
            #     # crossFiftyEma = [None] #Initial value used for the crossover
            #     # # crossFiftyEma.extend(tulipy.crossover(data_market_hours['close'].values, data_market_hours['ema50'].values))
            #     # crossFiftyEma.extend(tulipy.crossover(data_market_hours['close'].values, data_market_hours['ema50'].values))
            #     # # crossFiftyEma = numpy.append(crossFiftyEma, 0, None, axis=0) #Append 1 in the beginning to account for lost val
            #     # data_market_hours['crossFiftyEma'] = crossFiftyEma

            #     # print(data_market_hours)
            #     # sys.exit(1)
            #     # buySellSignals = []
            #     # for i in range(len(data_market_hours)):
            #     #     if data_market_hours['trendingAboveEma'][i] == posDir and data_market_hours['trendingAboveEmaMonth'][-1] == posDir and data_market_hours['generalSlope'][i] > 0 and data_market_hours['crossBuySellMacd'][i] == posDir and data_market_hours['close'][i] > data_market_hours['ema200'][i]:
            #     #         buySellSignals.append(posDir)
            #     #     elif data_market_hours['trendingAboveEma'][i] == negDir and data_market_hours['trendingAboveEmaMonth'][-1] == negDir and data_market_hours['generalSlope'][i] < 0 and data_market_hours['crossBuySellMacd'][i] == negDir and data_market_hours['close'][i] < data_market_hours['ema200'][i]:
            #     #         buySellSignals.append(negDir)
            #     #     else:
            #     #         buySellSignals.append(neutral)


            #     buySellSignals = []
            #     for i in range(len(data_market_hours)):
            #         if data_market_hours['trendingAboveEma'][i] == posDir and data_market_hours['generalSlope'][i] > 0 and data_market_hours['crossBuySellMacd'][i] == posDir and data_market_hours['close'][i] > data_market_hours['ema200'][i]:
            #             buySellSignals.append(posDir)
            #         elif data_market_hours['trendingAboveEma'][i] == negDir and data_market_hours['generalSlope'][i] < 0 and data_market_hours['crossBuySellMacd'][i] == negDir and data_market_hours['close'][i] < data_market_hours['ema200'][i]:
            #             buySellSignals.append(negDir)
            #         else:
            #             buySellSignals.append(neutral)

                    



            #     data_market_hours['buySellSignals'] = buySellSignals

                

                # print(f"Emadir {data_market_hours['emasSameDir'][-1]} trendingEma {data_market_hours['trendingAboveEma'][-1]} movingSlope {data_market_hours['movingSlope'][-1]} buySellSignals {data_market_hours['buySellSignals'][-1]}")
                # sys.exit(1)


            ################################################################################################################################################
            #NOT BACKTESTING
            ################################################################################################################################################    
            # for i in range(1, len(data_market_hours)):
            #     pass
                #DEALING WITH emas GOING SAME DIRECTION
                #ema50 - previous ema50 is greater than 0 (going up) repeated for ema9 and 200. done to see if it's below 0 to see if negative trending
                # if (data_market_hours['ema50'][i] - data_market_hours['ema50'][i-1] > 0 and data_market_hours['ema9'][i] - data_market_hours['ema9'][i-1] > 0 and data_market_hours['ema200'][i] - data_market_hours['ema200'][i-1] > 0):
                #     emasSameDir.append(posDir) #All emas greater than their past candle
                # elif (data_market_hours['ema50'][i] - data_market_hours['ema50'][i-1] < 0 and data_market_hours['ema9'][i] - data_market_hours['ema9'][i-1] < 0 and data_market_hours['ema200'][i] - data_market_hours['ema200'][i-1] < 0):
                #     emasSameDir.append(negDir)
                # else:
                #     emasSameDir.append(neutral)

            


                
            # emasGeneralTrend = [] #all emas moving in same direction CURRENTLY (using 1 candle back to get dir)
            # aboveAvgVolume = [] #if vol is above 20 period MA
            # candleBullOrBear = [] #Literally states if the candle is green or red
            # for i in range(len(data_market_hours)):
            #     # DEALING WITH CROSSOVER STUFF ON EMA50 AND EMA200 (just which crossover it's at rn, like ema50 > ema200 uptrend)
            #     if data_market_hours['ema9'][i] - data_market_hours['ema200'][i] > 0: #ema50 above
            #         emasGeneralTrend.append(posDir)
            #     elif data_market_hours['ema9'][i] - data_market_hours['ema200'][i] < 0:
            #         emasGeneralTrend.append(negDir)
            #     else:
            #         emasGeneralTrend.append(neutral) #They're the same (inconclusive)

            #     #DEALING WITH VOLUME
            #     if data_market_hours['volume'][i] > data_market_hours['avgVolume'][i]:
            #         aboveAvgVolume.append(posDir) #Positive can mean good for both up and downtrends since above avg volume means trend continuation
            #     elif data_market_hours['volume'][i] < data_market_hours['avgVolume'][i]:
            #         aboveAvgVolume.append(negDir)
            #     else:
            #         aboveAvgVolume.append(neutral) #avgVol and volume are equal somehow

            #     #DEALING WITH IF IT'S BULL OR BEAR CANDLE
            #     if data_market_hours['close'][i] - data_market_hours['open'][i] > 0: #closed above where it opened, so it increased
            #         candleBullOrBear.append(posDir)
            #     elif data_market_hours['close'][i] - data_market_hours['open'][i] < 0:
            #         candleBullOrBear.append(negDir)
            #     else:
            #         candleBullOrBear.append(neutral)

            generalSlope = []
            # print(len(data_market_hours))
            #Gets the slope for the last 30 days
            for i in range(len(data_market_hours)):
                if i >= daysInPastGT:
                    generalSlope.append(tulipy.linregslope(data_market_hours['close'][i+1-daysInPastGT:i+1].values, daysInPastGT)[0])
                else:
                    generalSlope.append(None)

            data_market_hours['generalSlope'] = generalSlope
            # print(linregslope)
            # sys.exit(1)
                




            
            trendingAboveEmaDay = [None for i in range(barsInPast)]
            for i in range(barsInPast, len(data_market_hours)):
                startingVal = i-barsInPast #This is like a moving box. We always want to check X bars back for every one bar
                aboveEma = 0
                belowEma = 0
                allChecks = 0
                # if data_market_hours['close'][i]
                for j in range(startingVal, i):
                    if data_market_hours['close'][j] - data_market_hours['ema200'][j] > 0: #A close price above the ema200
                        aboveEma += 1
                    elif data_market_hours['close'][j] - data_market_hours['ema200'][j] < 0:
                        belowEma += 1
                    allChecks += 1 #Everytime we check a point

                #If it's 80% above the ema200
                if (aboveEma/allChecks) > 0.80:
                    trendingAboveEmaDay.append(posDir)
                elif (belowEma/allChecks) > 0.80:
                    trendingAboveEmaDay.append(negDir)
                else:
                    trendingAboveEmaDay.append(neutral)
            
            data_market_hours['trendingAboveEma'] = trendingAboveEmaDay


            percentChange = talib.ROC(data_market_hours['close'].values, 1)
            # print(percentChange)
            # print(type(percentChange))
            # print(len(percentChange))
            # print(len(data_market_hours))
            # sys.exit(1)
            # percentChange = numpy.insert(percentChange, 0, None, axis=0)

            data_market_hours['percentChange'] = percentChange 
            # print(data_market_hours) 

            # sys.exit(1)


        


            # buySellSignals = []
            # for i in range(len(data_market_hours)):
            #     if data_market_hours['trendingAboveEma'][i] == posDir and data_market_hours['generalSlope'][i] > 0 and data_market_hours['crossBuySellMacd'][i] == posDir and data_market_hours['close'][i] > data_market_hours['ema200'][i] and data_market_hours['percentChange'][i] <= tooBigAMove:
            #         buySellSignals.append(posDir)
            #     elif data_market_hours['trendingAboveEma'][i] == negDir and data_market_hours['generalSlope'][i] < 0 and data_market_hours['crossBuySellMacd'][i] == negDir and data_market_hours['close'][i] < data_market_hours['ema200'][i] and data_market_hours['percentChange'][i] >= -tooBigAMove:
            #         buySellSignals.append(negDir)
            #     else:
            #         buySellSignals.append(neutral)

        

            buySellSignals = []
            for i in range(len(data_market_hours)):
                if data_market_hours['trendingAboveEma'][i] == posDir and data_market_hours['generalSlope'][i] > 0 and data_market_hours['crossBuySellMacd'][i] == posDir and data_market_hours['close'][i] > data_market_hours['ema200'][i]:
                    buySellSignals.append(posDir)
                elif data_market_hours['trendingAboveEma'][i] == negDir and data_market_hours['generalSlope'][i] < 0 and data_market_hours['crossBuySellMacd'][i] == negDir and data_market_hours['close'][i] < data_market_hours['ema200'][i]:
                    buySellSignals.append(negDir)
                else:
                    buySellSignals.append(neutral)

                



            data_market_hours['buySellSignals'] = buySellSignals


            data_market_hours = data_market_hours.tail(2) #Only get last N days where we actually want to buy
            # print(data_market_hours)





                #REAL
                #################################################################################
               
                # copyLen = [0 for i in range(len(data_market_hours))]
                # data_market_hours['generalSlope'] = copyLen #Focus this to use on entries since all emas are in the CURRENT same direction
                # data_market_hours['trendingAboveEma'] = copyLen
                # data_market_hours['buySellSignals'] = copyLen

                
                # #Set the one general 30d slope
                # data_market_hours['generalSlope'][-1] = tulipy.linregslope(data_market_hours['close'][-daysInPastGT:].values, daysInPastGT)
                
                
                


                # # crossFiftyEma = [None] #Initial value used for the crossover
                # # crossFiftyEma.extend(tulipy.crossover(data_market_hours['close'].values, data_market_hours['ema50'].values))
                # # # crossFiftyEma = numpy.append(crossFiftyEma, 0, None, axis=0) #Append 1 in the beginning to account for lost val
                # # data_market_hours['crossFiftyEma'] = crossFiftyEma

                # aboveEma = 0
                # belowEma = 0
                # allChecks = 0
                # for i in range(len(data_market_hours)-barsInPast, len(data_market_hours)):
                    
                #     # if data_market_hours['close'][i]
                #     if data_market_hours['close'][i] - data_market_hours['ema200'][i] > 0: #A close price above the ema200
                #         aboveEma += 1
                #     elif data_market_hours['close'][i] - data_market_hours['ema200'][i] < 0:
                #         belowEma += 1
                #     allChecks += 1 #Everytime we check a point

                # #If it's 80% above the ema200
                # if (aboveEma/allChecks) > 0.80:
                #     data_market_hours['trendingAboveEma'][-1] = posDir
                # elif (belowEma/allChecks) > 0.80:
                #     data_market_hours['trendingAboveEma'][-1] = negDir
                # else:
                #     data_market_hours['trendingAboveEma'][-1] = neutral



                # # aboveEma = 0
                # # belowEma = 0
                # # allChecks = 0
                # # for i in range(len(data_market_hours)-daysInPastGT, len(data_market_hours)):
                    
                # #     # if data_market_hours['close'][i]
                # #     if data_market_hours['close'][i] - data_market_hours['ema200'][i] > 0: #A close price above the ema200
                # #         aboveEma += 1
                # #     elif data_market_hours['close'][i] - data_market_hours['ema200'][i] < 0:
                # #         belowEma += 1
                # #     allChecks += 1 #Everytime we check a point

                # # #If it's 80% above the ema200
                # # if (aboveEma/allChecks) > trendingAboveEmaMonthlyPercentage:
                # #     data_market_hours['trendingAboveEmaMonth'][-1] = posDir
                # # elif (belowEma/allChecks) > trendingAboveEmaMonthlyPercentage:
                # #     data_market_hours['trendingAboveEmaMonth'][-1] = negDir
                # # else:
                # #     data_market_hours['trendingAboveEmaMonth'][-1] = neutral

                
                

                # #Checking data_market_hours['crossFiftyEma'][-1] == posDir everytime because 1 in this case means it crossed at a point
                # if data_market_hours['trendingAboveEma'][-1] == posDir and data_market_hours['generalSlope'][-1] > 0 and data_market_hours['crossBuySellMacd'][-1] == posDir and data_market_hours['close'][-1] > data_market_hours['ema200'][-1]:
                #     data_market_hours['buySellSignals'] = posDir
                # elif data_market_hours['trendingAboveEma'][-1] == negDir and data_market_hours['generalSlope'][-1] < 0 and data_market_hours['crossBuySellMacd'][-1] == negDir and data_market_hours['close'][-1] < data_market_hours['ema200'][-1]:
                #     data_market_hours['buySellSignals'][-1] = negDir
                # else:
                #     data_market_hours['buySellSignals'][-1] = neutral

                #REALLLLLLLLLL
                ###############################################################


                # print(f"Emadir {data_market_hours['emasSameDir'][-1]} trendingEma {data_market_hours['trendingAboveEma'][-1]} movingSlope {data_market_hours['movingSlope'][-1]} buySellSignals {data_market_hours['buySellSignals'][-1]}")
                # sys.exit(1)
            
 


            
            
            # print(data_market_hours) #dojis breakouts emasCrossing emasSameDir emasGeneralTrend aboveAvgVolume candleBullOrBear
            data_market_hours = data_market_hours.dropna()
            if shouldBacktest:
                for index, row in data_market_hours.iterrows():
                    cursor.execute("""
                        INSERT INTO globalBuySell (stock_id, datetime, open, high, low, close, volume, atr, buySellSignals)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (stock_ids[symbol], index.tz_localize(None).isoformat(), row['open'], row['high'], row['low'], row['close'], row['volume'], float(row['atr']), row['buySellSignals']))
                    

            

            




           


            # try:
            #     #IF the distance between the close price and the prior support line is LESS THAN the distance between the close and the resistance line, then there's more money to be made heading UPWARD SINCE THERE'S NO CLOSEBY RESISTANCE, so goingToResistance should be true
            #     if abs(levels_valsOnly[closeInd-1] - levels_valsOnly[closeInd]) < abs(levels_valsOnly[closeInd+1] - levels_valsOnly[closeInd]):
            #         goingToResistance = True #BUY since more money to be made at higher resistance
            #     elif abs(levels_valsOnly[closeInd-1] - levels_valsOnly[closeInd]) > abs(levels_valsOnly[closeInd+1] - levels_valsOnly[closeInd]):
            #         goingToResistance = False #SELL since close to resistance, and it could fall back to support
            #     else:
            #         #If the resistance distance is the same, we're going to follow the trend
            #         if trendingUp == True:
            #             goingToResistance = trendingUp
            #         elif trendingDown == True:
            #             goingToResistance = trendingDown
            #         else:
            #             goingToResistance = "No trend and no supp/resistance"

            #     print(f"Support & Resistance used with prior data (Has more space to go up): {goingToResistance}")


            # except:
            #     # #No past resistance lines, so lets just assume that it's heading in whatever current direction it's heading (possibly going to the moon)
            #     # if trendingUp == True: #If it's trending up, just say it's going to "resistance" if it's going down it's not going towards resistance (down)
            #     #     goingToResistance = True
            #     # elif trendingDown == True:
            #     #     goingToResistance = False
            #     # else:
            #     #     goingToResistance = 'No resistance but no trend here' #Just a safety measure. goingToResistance shouldnt be either true/false if there's no trend and no resistance
                
            #     #Going to use fibonacci retracements https://github.com/Ranjitkumarsahu1436/Fibonacci-Retracement/blob/master/FIBONACCI%20RETRACEMENT.ipynb
            #     #MaxMin
                
            #     #We're using 50 cents for retracements
            #     retracementVal = 0.50

            #     #If it's farther from resistance, it has more space to go up. If it's less than, then it
            #     support = abs((int(data_market_hours['close'][-1]) - retracementVal)) #Distance between the close price and the retracement value
            #     resistance = abs((int(data_market_hours['close'][-1]) + retracementVal))
            #     # print(f"{data_market_hours['close'][-1]} {belowRes} {aboveRes}")
            #     # sys.exit(1)
            #     distBelowRes = abs(data_market_hours.close[-1] - support) #Distance between support and close price
            #     distAboveRes = abs(resistance - data_market_hours.close[-1])#Distance between resistance and close price

            #     if distAboveRes > distBelowRes:
            #         goingToResistance = True 
            #     elif distAboveRes < distBelowRes:
            #         goingToResistance = False
            #     else:
            #         #If the resistance distance is the same, we're going to follow the trend
            #         if trendingUp == True:
            #             goingToResistance = trendingUp
            #         elif trendingDown == True:
            #             goingToResistance = trendingDown
            #         else:
            #             goingToResistance = "No trend and no supp/resistance"

            #     print(f"{data_market_hours['close'][-1]} {distBelowRes} {distAboveRes}")
            #     print(goingToResistance)
            #     # sys.exit(1)
                


                
                
                
                # priceMin = data_market_hours['close'][:].min()
                # priceMax = data_market_hours['close'][:].max()

                # #Difference
                # diff = priceMax - priceMin
                # #Fibonacci levels (Only need level1 (below min) and level3(above min))
                # level1 = priceMax - 0.236 * diff
                # level2 = priceMax - 0.382 * diff
                # level3 = priceMax - 0.618 * diff 

                # #Plot it
                # fig, ax = plt.subplots(figsize=(15,5))

                # ax.plot(data_market_hours.index, data_market_hours.close)

                # #Plotting the levels
                # ax.axhspan(priceMax, level3, alpha=0.5, color='powderblue')
                # plt.xlabel('Price')
                # plt.ylabel("Date")
                # plt.title("Fibonacci")
                # plt.show()


                # print(priceMin)
                # print(priceMax)
                
                # sys.exit(1)

           
            
            
            #FIX: take 25% off the trade when it reaches TP of reward ratio = 1 and move stoploss to break even, then set TP of reward ratio of 2

            #buying take profits
            #Note: 

            take_profit_buy = data_market_hours['close'][-1] + (data_market_hours['atr'][-1] * reward)
            stop_loss_buy =  data_market_hours['close'][-1] - (data_market_hours['atr'][-1] * risk)

            # print(f"{data_market_hours['close'][-1]} tp {take_profit_buy} sl {stop_loss_buy}")
            # sys.exit(1)

            #Take profits for selling
            take_profit_sell = data_market_hours['close'][-1] - (data_market_hours['atr'][-1] * reward)
            stop_loss_sell =  data_market_hours['close'][-1] + (data_market_hours['atr'][-1] * risk)

            # print(f"SELL {symbol} {data_market_hours.index[-1]}\n")
            #Buying
            ################################################
            #if there's a doji candle previously (never check current doji). This is just one method to lookout for a buy
            # (self.data.l.dojis[-1] == 100 or self.data.l.dojis[-1] == -100) and self.data.l.breakouts[0] == 100 and self.data.l.aboveAvgVolume[0] == 1 and self.iterDayTrades < self.threeDayTrades:
            # if (data_market_hours['dojis'][-2] == 100 or data_market_hours['dojis'][-2] == -100 or data_market_hours['dojis'][-3] == 100 or data_market_hours['dojis'][-3] == -100) and data_market_hours['breakouts'][-1] == 100 and data_market_hours['aboveAvgVolume'][-1] == 1 and data_market_hours['emasSameDir'][-1] == 1:
            # print(existing_order_symbols)
            # sys.exit(1)
            # buyOrSellStock(symbol, 'buy', take_profit_buy, stop_loss_buy, actuallyTrade)
            # sys.exit(1)
            if data_market_hours['buySellSignals'][-1] == posDir and symbol not in existing_order_symbols:
                buyOrSellStock(symbol, 'buy', take_profit_buy, stop_loss_buy, actuallyTrade)
                messages.append(f"BUY {symbol} {data_market_hours.index[-1]} MACD cross, trending up and above EMA \n")
                print(f"BUY {symbol}")

            #selling
            ###############################################
            # self.data.l.emasSameDir == -1
            # if (data_market_hours['dojis'][-2] == 100 or data_market_hours['dojis'][-2] == -100 or data_market_hours['dojis'][-3] == 100 or data_market_hours['dojis'][-3] == -100) and data_market_hours['breakouts'][-1] == -100 and data_market_hours['aboveAvgVolume'][-1] == 1 and data_market_hours['emasSameDir'][-1] == -1:
            if data_market_hours['buySellSignals'][-1] == negDir and symbol not in existing_order_symbols and symbol != 'TSLA':
                buyOrSellStock(symbol, 'sell', take_profit_sell, stop_loss_sell, actuallyTrade)
                messages.append(f"SELL {symbol} {data_market_hours.index[-1]} MACD cross, trending down and below EMA \n")
                print(f"SELL {symbol}")

                
            

 
    
                    


                
                   


                                                        
        except Exception as e:
            #print(len(avgVolNoNones))
            #print(len(data_market))
            exc_type, exc_obj, exc_tb = sys.exc_info()

            # print(f"For date {data_market_hours.index[-1]} probably close price was below all support/resistance")
            print(f"{e} \n Line {exc_tb.tb_lineno}")
            traceback.print_exc()
            # sys.exit(1)
            # 





with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD) #Login
    email_message = f"Subject: Executed Tradebot: {current_date}\n\n" #Our email subject

    email_message += "\n\n".join(messages) #Our message
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message) #From, to, message (sending to ourself)
    print("End execution")

      





            

            
            





conn.commit() #Commit our historical minute data to the sqlite3 database



