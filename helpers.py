import alpacaConfig as config 
import math
import alpaca_trade_api as tradeapi #alpaca
import numpy as np
import sys




###############INPUTS
####################################################################
stoplossAtrAway = 1
keepProfitPercent = 0.10 #Keep this percent of profits if the trade goes in your favor (this is just limit prices, NOT risk/reward ratio, so just think of this as profitting instead of going in the negatives potentially (securing profits), thus, lower values like 0.1 are fine)
# currentOrdersBeforeChecking = 2 #only X orders before it can only check the order -> this is debunked with the new and improved view the actual sent out market orders. If it's 3, let it be (pdt rule)
timeInterval = 15 #We're using 15 minutes -> only supports 5min and 15min bars. To add functionality for more, just add that timeframe data in macdSignalNotifier.py, update daysAwayMultiple, and in updateOrder, just change the liquidation script
percentMoneyForEachTrade = 0.01 #Percent of your buying power for every trade
####################################################################



#Calculated vars
# ############################
if timeInterval == 5: #If 5min abrs
    daysAwayMultiple = 18 #Go a multiple of 18 in the past
elif timeInterval == 15: #15m bars
    daysAwayMultiple = 18   #30
else:
    daysAwayMultiple = 18 #Default historical data



api = tradeapi.REST(config.apiKey, config.secretKey, base_url=config.baseUrl)



accEquity = float(api.get_account().cash) #Like 10k



# print((api.get_account()))
# sys.exit(1)
# print(accEquity)
# sys.exit(1)

#We only want to use 10% of our balance, so we seperate this into tradingmoney
tradingBalance = accEquity * percentMoneyForEachTrade #YEah whatever change this value whenever necessary (very professional) -> 1800 dollars =  0.018 percent

############################

#print(accEquity)
#print(tradingBalance)


#We want our stocks to only take 10% of our portfolio, so we calculate the quantity of stocks we buy
def calculate_quantity(price):
    #math.floor(10000 price / 300 price = 3.3 shares)
    quantity = math.floor(float(tradingBalance) / price) #The 10,000 is 10% of our paper trading account. Make this value 10% of your normal account
    return quantity


sampleArr = np.array([1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,4,12,2])




#print(sampleArr)
#sys.exit(1)

#Takes a numpy array of volume with 20 extra values to mark as the period
def calculate_avg_volume20(vol_np):
    rectOffset = 0 #Starts at 1 so it starts after the period ends, so we can assign the last value to the actual average
    periodLen = 20 #The period length


    avgsList = np.array([None for i in range(periodLen)]) #Fill up an array of None values originally to mark the period
    #print(type(avgsList))
    #sys.exit(1)

    #20 is the period we're calculating the average volume in

    #The +1 allows us to go to the last index within the timeperiod (this was just debugged)
    amountOfRects = len(vol_np) - periodLen +1 #this is just how many numbers there are besides the first initial period, which is outsie of market hours
    #print(amountOfRects)
    
    for i in range(0, amountOfRects):
        indCurrentStart = rectOffset
        indCurrentEnd = periodLen + rectOffset #rectOffset is just the offset so it keeps indexing a rectangle
        avg_vol = np.average(vol_np[indCurrentStart:indCurrentEnd])
        

   


        #print(vol_np[indCurrentStart:indCurrentEnd])


        avgsList = np.append(avgsList,avg_vol)

        # print(vol_np[indCurrentStart:indCurrentEnd])
        # print(avgsList)
        
        rectOffset += 1
        #sys.exit(1)

    return avgsList

    

#print(calculate_avg_volume20(sampleArr))



#close numpy array (share price), volume at that cooresponding share price (volume same length as the share price)
def calculate_vwap20(high_np, low_np, close_np, volume_np, period):
    """
    Calc vwap

    Summation(E) Number of shares * share price / total shares

    Ex: 11$ shares for 200, 100 shares for 10$, and 300 shares for 8$

    We do

    (11 * 200) + (10 * 100) + (8 * 300) / (100+200+300) = 9.333 VWAP

    """

    vwapList = np.array([None for i in range(period)]) #Fill up an array of None values originally to mark the period

    rectOffset = 0 #Starts at 1 so it starts after the period ends, so we can assign the last value to the actual average

    periodLen = period #this is still a 20 period since indexing is weird


    #The +1 allows us to go to the last timeperiod in the index (this was debugged)
    amountOfRects = len(close_np) - periodLen+1  #this is just how many numbers there are besides the first initial period, which is outsie of market hours
    

    #print(amountOfRects)
    for i in range(amountOfRects):
        indCurrent = rectOffset #Just update the square we're accessing within the list
        indEnd = periodLen + rectOffset

        tempHigh = high_np[indCurrent:indEnd]  #Just setting the rectangle (period) we're working with
        tempLow = low_np[indCurrent:indEnd]
        tempClose = close_np[indCurrent:indEnd]
        tempVol = volume_np[indCurrent:indEnd]



        summationNumerator = 0 #Calculates numerator for VWAP

        for j in range(len(tempClose)): #Just picked a list here since they're both same size. We're just going to start doing vwap calculations
            sharePrice = (tempHigh[j] + tempLow[j] + tempClose[j])/3#(H+L+C)/3 is typical price, close to the share price for vwap
            summationNumerator += (sharePrice * tempVol[j]) #Share price * volume

        #Now we divide by the total volume within that row and append that to the VWAP list
        vwapList = np.append(vwapList, summationNumerator / (np.sum(tempVol, axis=0)))
        #print(f"SharePrice: {sharePrice} --> AppendedVwap {summationNumerator / (np.sum(tempVol, axis=0))}")


        rectOffset += 1

    return vwapList

#This should be a period (it should be X values from the past)
#This expects you to find the date of the recent market hours (I explained how to do this in historical_backtest_vwma5.py)
#endMarketIndBefore is the LAST INDEX for the previous market hours within currentData. For example, this could be the index at 16:00pm for 11/22/2020.
#startMarketIndCurrent and endMarketIndCurrent are the index (epoches) for the current market. Ex: startMarketIndCurrent's index is 11/23/2020's 9:30am and endMarketIndCurrent is at 16:00pm (4:00pm)
def make_previous_market_bars(currentData, period, endMarketIndBefore, startMarketIndCurrent, endMarketIndCurrent):
    #It's 18 instead of 19 since we want to include 1 less to include the current bar
    period -= 1 #Minused by 2 so it removes 1 from the beginning period when we add 1 to the end to include the 4pm bar
    pastAndPresent = list(currentData[endMarketIndBefore-period:endMarketIndBefore+1].values) #get the previous day's LATEST market hour values
    pastAndPresent.extend(currentData[startMarketIndCurrent:endMarketIndCurrent].values) #Add the current volume to that
    pastAndPresent = np.asarray(pastAndPresent) #Make it a numpy list

    """
    #It's 18 instead of 19 since we want to include 1 less to include the current bar
    prevMarketVolAndCurrent = list(data.volume[endMarketIndBefore-18:endMarketIndBefore+1].values) #get the previous day's LATEST market hour values
    prevMarketVolAndCurrent.extend(data.volume[startMarketInd:endMarketInd].values) #Add the current volume to that
    prevMarketVolAndCurrent = numpy.asarray(prevMarketVolAndCurrent) #Make it a numpy list
    data is a dataframe. This is just how we would implement it within 1 case (period here is 20. We have 18 there since we did 20-2 and we just add 1 more at the end so we get 19 values. We include a current value)
    """

    return pastAndPresent



def make_previous_market_bars_daily(currentData, period, startMarketIndCurrent):
    pastAndPresent = list(currentData[-period:len(currentData)-1].values) #Simply go back to the period and go up to the second to last value
    # print(pastAndPresent)
    # print(len(pastAndPresent))
    # sys.exit(1)
    pastAndPresent.extend(currentData[startMarketIndCurrent:startMarketIndCurrent+1].values) #Add the current volume to that (inclusive)
    # print(pastAndPresent)
    # print(len(pastAndPresent))
    # sys.exit(1)
    pastAndPresent = np.asarray(pastAndPresent) #Make it a numpy list

    return pastAndPresent





highSample = [2 for i in range(25)] 
lowSample = [1 for i in range(25)] 
closeSample = [1.5 for i in range(25)] #Lists are the same length
volSample = [i for i in range(0, 1000, 40)] #1000/40 = 25 elements
#calculate_vwap20(highSample, lowSample, closeSample, volSample)


#https://ibb.co/zSdMT2V to get the end previous market volume, and to confirm that 70270 is first bar at 9:30am
# https://ibb.co/2MpLKgK -> In-detail explanation of the output https://docs.google.com/document/d/1nHp-wE26dRjH3TDeadJ8Ag-TIxxBFOjcTTdxktfzNUo/edit -> Sign into the normal email you use (check alpacaConfig)
#marketVolData = [ 46565,  21524,  17025,  15224,  11474,   9261,   6753,  57259,  12886,19071,  13197,  13075,  19998,  22791,  27710,  21972,  31911, 119518, 6271,  46827,  16567,  13616,  14972,  16485,  16137,  19643,  14083, 10426,  10581,  15620,  10536,  12888,  13693,   8813,  16476,  87966, 10880, 101136, 110943,  36360,  28099,  25557,  33688,  35322, 107034]
#calculate_avg_volume20(marketVolData)

#print(calculate_quantity(1000))



#Candlestick patterns
#listOfPatterns = [0,0,0,0,0,100,0,0,0,0,-100]
def analyzePattern(listOfPatterns):
    #What we're doing: Across each minute for each pattern, we're just going to add the different assumptions:
    #And put that all into a list with the sums. 


    #Since all inner lists have same size, we're going to use numpy vectorization
    #Make it a 2d array
    arr = np.array(listOfPatterns)

    #Sum ACROSS first axis (vertically) -> gets each corresponding position on the inner lists across each index) 
    res = arr.sum(axis=0).tolist()

    for i in range(len(res)):
        if res[i] >= 100: #Since the values were summed, we're just getting the most dominant assumption here
            res[i] = 100
        elif res[i] <= -100:
            res[i] = -100
    
    return res


#This is specific to the specified timeframe in the variable timeInterval
def stackDataNotDaily(inputDf, iteratorDate):
    #Just copy paste the above code from under date (this isn't a function sorry mate)
    data = api.polygon.historic_agg_v2(symbol, timeInterval, 'minute', _from=iteratorDate-timedelta(days=daysDist), to=iteratorDate).df #Get the data from that start_date to the end_date for the 5min bar date
    print(f"=== {symbol} Fetching from {(iteratorDate-timedelta(days=daysDist))} to {iteratorDate} with {timeInterval}min bars")
    data_mask = []
    import datetime
    for dat in data.index:
        data_mask.append(dat.time() >= datetime.time(9,30,0) and dat.time() < datetime.time(16,0,0)) #Only get market hours
    data_market = data.loc[data_mask]



    


#For whichever timeframe you use, this will use all of those bars and put that into the daily timeframe (it just makes it 1 bar)
def stackDataDailyEveryTimeFrame(inputDf, iteratorDate):
    #Just copy paste the above code from under date (this isn't a function sorry mate)
    data = api.polygon.historic_agg_v2(symbol, timeInterval, 'minute', _from=iteratorDate-timedelta(days=daysDist), to=iteratorDate).df #Get the data from that start_date to the end_date for the 5min bar date
    print(f"=== {symbol} Fetching from {(iteratorDate-timedelta(days=daysDist))} to {iteratorDate} with {timeInterval}min bars")
    data_mask = []
    import datetime
    for dat in data.index:
        data_mask.append(dat.time() >= datetime.time(9,30,0) and dat.time() < datetime.time(16,0,0)) #Only get market hours
    data_market = data.loc[data_mask]



    
    # Resample it to dayily time
    data_market = data_market.resample('1D', closed='right', label='right').agg(
        {'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
        }
    )



    # #CHANGE THE ACTUAL TIME IN THE INDEXES
    for dat in range(len(data_market.index)):
        #dat.date() -= timedelta(days=1) #When we resample it, it pushes the day 1 up incorrectly
        datReplaceTime = data_market.index[dat].replace(hour=15, minute=45)
        datReplaceTime -= timedelta(days=1)
        data_market.index.values[dat] = datReplaceTime #Replace the time at the index with the time we want to trade at
        #print(dat) #Doesn't include weekends/holidays


#Stolen function from backtest https://pypi.org/project/Backtesting/
"""
def crossover(series1: Sequence, series2: Sequence) -> bool:
    
    Return `True` if `series1` just crossed over
    `series2`.

        >>> crossover(self.data.Close, self.sma)
        True
    
    series1 = (
        series1.values if isinstance(series1, pd.Series) else
        (series1, series1) if isinstance(series1, Number) else
        series1)
    series2 = (
        series2.values if isinstance(series2, pd.Series) else
        (series2, series2) if isinstance(series2, Number) else
        series2)
    try:
        return series1[-2] < series2[-2] and series1[-1] > series2[-1]
    except IndexError:
        return False

"""

volumeFiveMin = [  7159,  13352,  11345,  11810,  10643,   8290,   9521,  13715,  11160, 12624,   7646,   8865,  16088,  27641,  16866,  21455,  33515, 142765,23181, 42381,  11605,  16284,   9691,  10810,  15795,   7358,  12593,   7898,17638,  12002,  13463,  15715,  11882,   7664,   9703,   9969,   9607,9442,  15495,  12293,   8007,  15971,   5834,  10508,   6947,  13769, 6450,   6781,  19404,  25589,   8528,  20793,  10216,  15469,  17792, 11558,   6513,  16361,  13048,  15786,   9486,  16046,   8245,  15705, 16692,  22209,  15213,   5868,  17140,  15197,   8523,   8576,  13265, 16519,  25111,  20443,   9128,   9360,   8675,  20847,  14288,  27712, 19440,  53950,  11929,  22718,  18704,  27623,  17579,  14572,  16927, 17694,  29671,  21665,  32426,  44937, 100760]

