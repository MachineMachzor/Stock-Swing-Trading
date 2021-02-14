import alpacaConfig as config 
import sqlite3 
import backtrader, pandas, sqlite3 
import backtrader.feeds as btfeeds
from datetime import date, datetime, time, timedelta
import backtrader
import sys
import tulipy
import numpy
from statistics import mean #For the average

inputCash = 1000

#These are the performance variables that will be really useful for evaluating multiple stocks
big30Percentwins = 0 #Wins where equity is >= 30%
big20PercentWins = 0
big10PercentWins = 0
small10PercentLose = 0
small20PercentLose = 0
small30PercentLose = 0
totalWins = 0
totalLoses = 0
totalStocks = 0


#Global variables for all of the winrates
strike_rate = []
pnl_net = []
sqn = []
total_open = 0
total_closed  = 0
total_won = 0
total_lost = 0
win_streak = []
lose_streak = []


#https://backtest-rookies.com/2017/06/11/using-analyzers-backtrader/
"""
1.6 – 1.9 Below average
2.0 – 2.4 Average
2.5 – 2.9 Good
3.0 – 5.0 Excellent
5.1 – 6.9 Superb
7.0 – Holy Grail?

"""


def printTradeAnalysis(analyzer):
    global total_open, total_closed, total_won, total_lost, win_streak, lose_streak

    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    #Get the results we are interested in
    try:
        total_open += analyzer.total.open
        total_closed += analyzer.total.closed
        total_won += analyzer.won.total
        total_lost += analyzer.lost.total
        win_streak.append(analyzer.streak.won.longest)
        lose_streak.append(analyzer.streak.lost.longest)
        # pnl_net = round(analyzer.pnl.net.total,2)
        pnl_net.append(round(analyzer.pnl.net.total,2))
        # strike_rate = (total_won / total_closed) * 100 #winrate
        strike_rate.append((total_won / total_closed) * 100)
        
        strike_rate_score = round(mean(strike_rate),2)
        pnl_net_score = round(mean(pnl_net),2) #Just taking the mean of all of these to get the average winrate/score
        
        #Designate the rows
        h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
        h2 = ['Win Rate','Win Streak', 'Losing Streak', 'PnL Net'] #WinRate = Strike Rate
        r1 = [total_open, total_closed,total_won,total_lost]
        r2 = [strike_rate_score, round(mean(win_streak),2), round(mean(lose_streak),2), pnl_net_score]
        #Check which set of headers is the longest.
        if len(h1) > len(h2):
            header_length = len(h1)
        else:
            header_length = len(h2)
        #Print the rows
        print_list = [h1,r1,h2,r2]
        row_format ="{:<15}" * (header_length + 1)
        print("Trade Analysis Results:")
        for row in print_list:
            print(row_format.format('',*row))
    except:
        print("No trades")


def printSQN(analyzer):
    global sqn
    # sqn = round(analyzer.sqn,2)
    try:
        sqn.append(round(analyzer.sqn,2))
        print('SQN: {}'.format(mean(sqn)))
    except:
        print("No trades, so no SQN")


class StratData(btfeeds.PandasData):
    lines = ('volume', 'atr', 'buySellSignals')

    params = (
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
        ('atr', 'Atr'),
        ('buySellSignals', 'BuySellSignals')
    )



#Extends backtrader.Strategy in order to backtest
class RsiEmaCandle(backtrader.Strategy):
    global totalLoses


    params = dict(
        # rsi_period = 14, #First 14 minutes. We'll need 14 minutes before trading
        # ema_period = 200, #First 200 minutes. Note: We will go back in pre-market hours to get some of the data
        # trail = 0.3 #When 30% of profits are lost, stoploss will trigger

    )

    #Just initialize values
    def __init__(self):
        self.candles_prev = 0 #Keeps track of how many candles pass (we don't trade until X number of candles pass)
        

        self.iterDayTrades = 0
        self.threeDayTrades = 3
        self.risk = 1
        self.reward = 0.1

        self.trade = 'neutral'
        self.bought_today = False

        

    def log(self, txt, dt=None):
        if dt is None:
            dt = self.datas[0].datetime.datetime() #gets the most recent date
        print('%s, %s' % (dt, txt))

    #This part is within the documentation. Notifies you of the order
    def notify_order(self, order):
        # if order.status in [order.Submitted, order.Accepted]:
        #     return #If the order was already submitted or accepted, return since we don't wanna repeat that order
        
        # # Check if the order has been completed (order is done)
        # if order.status in [order.Completed]:
        #     order_details = f"{order.executed.price}, Cost: {order.executed.value}, Commission {order.executed.comm}"
        #     if order.isbuy():
        #         self.log(f"BUY EXECUTED, Price {order_details}")
        #     else: #Order was a sell
        #         self.log(f"SELL EXECUTED, Price: {order_details}")
        # elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        #     self.log("Order Canceled/Margin/Rejected")
        

        self.order = None #None the order
            


    def next(self):
        current_bar_datetime = self.data.num2date(self.data.datetime[0]) #Current date
        previous_bar_datetime = self.data.num2date(self.data.datetime[-1]) #Previous date

        if current_bar_datetime.date() != previous_bar_datetime.date():
            self.bought_today = False #On a new day, state that we haven't bought for this bar
            self.iterDayTrades = 1 #Reset daytrades
            # self.trade = 'neutral' #Didnt buy or sell yet

        # start_time = time(9,30,0) #Starts at 9:30am
        # dt = datetime.combine(date.today(), start_time) + timedelta(minutes=self.p.rsi_period) #Combines the date with the time, but adds the rsi_period (14) this data is horrible btw.
        # #print(dt)
        # opening_range_end_time = dt.time() #Gets the endtime after 15 minutes
        # #print(opening_range_end_time) prints 9:44am
        # print(f"{current_bar_datetime} {self.data.l.atr[0]}")


        #Note: rsi_14 is needed because I wouldn't know how to calculate it at the beginning like I did with ema (rsi works weirdly)
        #if current_bar_datetime.time() >= start_time \
        #    and current_bar_datetime.time() < opening_range_end_time:
            #Within this rsi_period range (9:30-9:44am), so do nothing until this range ends
        #    pass
        #else:
            #Now update our rsi value, candle, and ema periods
            #print(self.data)
            
            
            
        #self.ema200_value = self.data.ema200[0] #200ema value
        #print(self.data.l.candlestickPatternDir[0]) 
        
        #Sees if X num of candles passes. Ex: this is 3, then it starts on the 4th candle
        if self.candles_prev >= 0: #We can't moniter a trade that late in the market       and current_bar_datetime.time() < time(15,45,0):

           

            #Don't trade against the market. Make sure these two align
            # print(f"rsiDaily {rsiDaily} rsiFourHours {rsiFourHours}")


        


            #Place stoploss at recent high/low (three candles back i guess) -> nah just use atr. Only go 1 away since we're using a small timeframe
            #During short position Exit when stochastic and rsi is oversold (rsi < 30 and (stochK and stochP < 20))
            #Buying, check if rsi is  -> just going to use atr for my stoploss. lower trading, set stoploss to a lesser value https://levelup.gitconnected.com/4-practical-methods-to-set-your-stop-loss-when-algo-trading-bitcoin-adb51b03849a
            #if rsi is indicating an uptrending market currently, the 4hr and 1d agree that it's an uptrend , and the previous 2 candles (current candle and 1 candle back) don't have macd sell signals, and the macd gives a buy signal on the current or previous candle, and if stochP and stochK is less than 20 on current or previous candle, and the current candle's stochP and stochK are less than 80 (we have to check this due explicitly since we used an or statement)
            # if self.data.l.rsi[0] > 50 and generalMarketDir == 1 and  (self.data.l.macd_buysell[0] != self.macd_sell) and (self.data.l.macd_buysell[-1] != self.macd_sell) and ((self.data.l.macd_buysell[0] == self.macd_buy) or (self.data.l.macd_buysell[-1] == self.macd_buy)) and ((self.data.l.stochP[0] < self.stochGoingUp) or (self.data.l.stochP[-1] < self.stochGoingUp)) and ((self.data.l.stochK[0] < self.stochGoingUp) or (self.data.l.stochK[-1] < self.stochGoingUp)) and self.data.l.stochP[0] < self.stochGoingDown and self.data.l.stochK[0] < self.stochGoingDown:
            #     print(f"Buy at {current_bar_datetime}")
            # elif self.data.l.rsi[0] < 50 and generalMarketDir == -1 and  (self.data.l.macd_buysell[0] != self.macd_buy) and (self.data.l.macd_buysell[-1] != self.macd_buy) and ((self.data.l.macd_buysell[0] == self.macd_sell) or (self.data.l.macd_buysell[-1] == self.macd_sell)) and ((self.data.l.stochP[0] > self.stochGoingDown) or (self.data.l.stochP[-1] > self.stochGoingDown)) and ((self.data.l.stochK[0] > self.stochGoingDown) or (self.data.l.stochK[-1] > self.stochGoingDown)) and self.data.l.stochP[0] > self.stochGoingDown and self.data.l.stochK[0] > self.stochGoingDown:
            #     print(f"Sell at {current_bar_datetime}")

            # if self.data.l.rsi[0] < 50 and self.data.l.stochP[0] < self.stochGoingUp and self.data.l.stochK[0] < self.stochGoingUp:
            #     print(f"Sell at {current_bar_datetime}"

            # if stochUptrend and self.data.l.rsi > 50 and self.data.l.macd_buysell[0] == self.macd_buy:
            #     print(f"Buy at {current_bar_datetime}")

     

            #Executing trades
            ################################################
            # if self.data.l.rsi[0] < 50 and generalMarketDir == -1 and stochDowntrend and macdSellSignal and not self.position:
            #     print(f"Sell at {current_bar_datetime}")
            #     self.sell_bracket(
            #         stopprice=self.data.l.close[0] + self.data.l.atr[0]*1,
            #         stopexec=backtrader.Order.StopTrail,
            #         trailpercent=0.8 #Trail for 30% of the profits
            #     )

            #Selling
            # if self.data.l.rsi[0] < 50 and generalMarketDir == -1 and macdSellSignal and self.iterDayTrades < self.threeDayTrades:
            #     self.sell_bracket(
            #     stopprice=self.data.l.close[0] + self.data.l.atr[0]*1,
            #     # stopexec=backtrader.Order.StopTrail,
            #     # trailpercent=0.8 #Trail for 30% of the profits
            #     )
            #     self.iterDayTrades += 1

        
            # # if self.order:
            # #     return
            # if self.position and self.data.l.rsi[0] > 50 and self.data.l.stochP[0] < self.stochGoingUp and self.data.l.stochK[0] < self.stochGoingUp:
            #     self.close()


            #Buying
            #if there's a doji candle previously (never check current doji). This is just one method to lookout for a buy
            ##################################################################################################
            
            # if (self.data.l.dojis[-1] == 100 or self.data.l.dojis[-1] == -100) and self.data.l.breakouts[0] == 100 and self.data.l.aboveAvgVolume[0] == 1 and self.data.l.emasSameDir == 1 and self.iterDayTrades < self.threeDayTrades:
            #     price = self.data.l.close[0]
            #     limitprice = price + (self.data.l.atr[0] * self.reward)
            #     stopprice = price - (self.data.l.close[0] * self.risk)
            #     self.order = self.buy_bracket(limitprice=limitprice, price=price, stoppprice=stopprice)
                
            #     self.trade = 'buying'
            #     self.iterDayTrades += 1


            if self.data.l.buySellSignals[0] == 1:
                price = self.data.l.close[0]
                limitprice = price + (self.data.l.atr[0] * self.reward)
                stopprice = price - (self.data.l.close[0] * self.risk)
                self.order = self.buy_bracket(limitprice=limitprice, price=price, stoppprice=stopprice)
                
                self.trade = 'buying'
                self.iterDayTrades += 1

            

            #Ema positive crossover positive
            # if (self.data.l.emasCrossing[0] == 1) and (self.data.l.emasGeneralTrend[0] == 1) and self.iterDayTrades < self.threeDayTrades:
            #     # print(f"{current_bar_datetime} StochPKsignal {self.data.l.stockPKSignals[0]} macdSignal {self.data.l.stockPKSignals[0]}")
            #     price = self.data.l.close[0]
            #     limitprice = price + (self.data.l.atr[0] * self.reward)
            #     stopprice = price - (self.data.l.close[0] * self.risk)
            #     self.order = self.buy_bracket(limitprice=limitprice, price=price, stoppprice=stopprice)
                
            #     self.trade = 'buying'
            #     self.iterDayTrades += 1

            #Doing breakout candles with ema trend
            # if self.data.l.breakouts[0] == 100 and self.data.l.aboveAvgVolume == 1 and self.data.l.emasSameDir == 1 and self.iterDayTrades < self.threeDayTrades:
            #     price = self.data.l.close[0]
            #     limitprice = price + (self.data.l.atr[0] * self.reward)
            #     stopprice = price - (self.data.l.close[0] * self.risk)
            #     self.order = self.buy_bracket(limitprice=limitprice, price=price, stoppprice=stopprice)
            
            #     self.trade = 'buying'
            #     self.iterDayTrades += 1

            ##################################################################################################



            #selling
            
            # if (self.data.l.dojis[-1] == 100 or self.data.l.dojis[-1] == -100) and self.data.l.breakouts[0] == -100 and self.data.l.aboveAvgVolume[0] == 1 and self.data.l.emasSameDir == -1 and self.iterDayTrades < self.threeDayTrades:
            #     price = self.data.l.close[0]
            #     limitprice = price - (self.data.l.atr[0] * self.reward)
            #     stopprice = price + (self.data.l.close[0] * self.risk)
            #     self.order = self.sell_bracket(limitprice=limitprice, price=price, stoppprice=stopprice)
                
            #     self.trade = 'selling'
            #     self.iterDayTrades += 1

            if self.data.l.buySellSignals[0] == -1:
                price = self.data.l.close[0]
                limitprice = price - (self.data.l.atr[0] * self.reward)
                stopprice = price + (self.data.l.close[0] * self.risk)
                self.order = self.sell_bracket(limitprice=limitprice, price=price, stoppprice=stopprice)
                
                self.trade = 'selling'
                self.iterDayTrades += 1

            

            ## Ema negative crossover
            # if (self.data.l.emasCrossing[0] == 1) and (self.data.l.emasGeneralTrend[0] == -1) and self.iterDayTrades < self.threeDayTrades:
            #     # print(f"{current_bar_datetime} StochPKsignal {self.data.l.stockPKSignals[0]} macdSignal {self.data.l.stockPKSignals[0]}")
            #     price = self.data.l.close[0]
            #     limitprice = price - (self.data.l.atr[0] * self.reward)
            #     stopprice = price + (self.data.l.close[0] * self.risk)
            #     self.order = self.sell_bracket(limitprice=limitprice, price=price, stoppprice=stopprice)
                
            #     self.trade = 'selling'
            #     self.iterDayTrades += 1 #Note: with 25k in ur account, you won't be limited to 3 daytrades thus makin more money (work at like mcdonalds or follow WSB for that 25k, actually transition to forex)

            #Doing breakout candles with ema trend
            # if self.data.l.breakouts[0] == -100 and self.data.l.aboveAvgVolume == 1 and self.data.l.emasSameDir == -1 and self.iterDayTrades < self.threeDayTrades:
            #     price = self.data.l.close[0]
            #     limitprice = price - (self.data.l.atr[0] * self.reward)
            #     stopprice = price + (self.data.l.close[0] * self.risk)
            #     self.order = self.sell_bracket(limitprice=limitprice, price=price, stoppprice=stopprice)
            #     self.trade = 'selling'
            #     self.iterDayTrades += 1



            #Close the buying trade if rsi indicates negative trend and stoch goes down to 20
            # if self.position and self.data.l.stockPKSignals[0] != 3 and self.trade == 'buying':
            #     self.close()
            #     self.trade = 'neutral'
            #     self.iterDayTrades += 1


            # print(int(self.data.l.macd_buysell[0]))
            

            
            # #Selling
            # if self.data.l.stockPKSignals[0] == 5 and self.trade == 'neutral' and not self.position:
                # # self.sell_bracket(
                # # stopprice=self.data.l.close[0] - self.data.l.atr[0]*2,
                # # limitprice=self.data.l.close[0] * 1.03
                # # # stopexec=backtrader.Order.StopTrail,
                # # # trailpercent=0.1,
                # # # stopexec=backtrader.Order.StopTrail,
                # # # trailpercent=0.8 #Trail for 30% of the profits
                # # )

                # # self.sell(stopprice=self.data.l.close[0] + self.data.l.atr[0]*1)
                # self.sell()
                # self.trade = 'selling'


            # #Close the buying trade if rsi indicates negative trend and stoch goes down to 20
            # if self.position and self.data.l.stockPKSignals[0] != 2 and self.trade == 'selling':
            #     self.close()
            #     self.trade = 'neutral'
            # else:
            #     if self.trade == 'selling':
            #         # print(f"{current_bar_datetime} Rsi {self.data.l.rsi[0]} StochPKsignal {self.data.l.stockPKSignals[0]} macdSignal {self.data.l.stockPKSignals[0]}")
                    # pass





            

        """
        if self.data.l.rsi_14[0] > 50 and self.data.l.candlestickPatternDir[0] == 100 and self.data.l.ema200[0] < self.data.l.close[0]:
            #If the rsi is greater than 50, a positive current candlestick, and the current close is greater than the ema200
            self.order = self.buy_bracket(
                stopprice=self.data.l.close[0] - (self.data.l.atr[0] * 2), #Stoploss
                price=self.data.l.close[0], #Buy price
                #limit=self.data.l.close[0] + (self.data.l.atr[0]*2), #Take profits (probably not that great)
                stopexec=backtrader.Order.StopTrail,
                trailpercent=self.p.trail #Trail for 30% of the profits
            )
        if self.data.l.rsi_14[0] < 50 and self.data.l.candlestickPatternDir[0] == -100 and self.data.l.ema200[0] > self.data.l.close[0]:
            #If the recent rsi_14 is less than 50 and the candlestickpattern is negative and the recent close is below the ema200
            self.order = self.sell_bracket(
                stopprice=self.data.l.close[0] + (self.data.l.atr[0] * 2), #Stoploss
                price=self.data.l.close[0], #Buy price
                limit=self.data.l.close[0] - (self.data.l.atr[0]*2), #Take profits (probably not that great)
                stopexec=backtrader.Order.StopTrail,
                trailpercent=self.p.trail #Trail for 30% of the profits
            )
        
        """
        # if self.data.l.rsi_14[0] > 50 and self.data.l.candlestickPatternDir[0] == 100 and self.data.l.ema200[0] < self.data.l.close[0]:
        #     #If the rsi is greater than 50, a positive current candlestick, and the current close is greater than the ema200
        #     self.order = self.buy()
        # else:
        #     if self.position and self.data.l.rsi_14 < 50:
        #         self.order = self.close()


        # if self.data.l.rsi_14[0] < 50 and self.data.l.candlestickPatternDir[0] == -100 and self.data.l.ema200[0] > self.data.l.close[0]:
        #     #If the rsi is greater than 50, a positive current candlestick, and the current close is greater than the ema200
        #     self.order = self.sell()
        # else:
        #     if self.position and self.data.l.rsi_14[0] > 50: #Buy it back if there's an rsi change
        #         self.order = self.close()

        

        



        # if self.position and current_bar_datetime.time() >= time(15,58,0):
        #     self.log("RUNNING OUT OF TIME - LIQUIDATING POSITION")
        #     self.close()

    

        #sys.exit(1)
        """
        self.candleDir = self.data.candlestickPatternDir[0] #Candlestick analysis value from buncho patterns. 1 == positve, -1 == negative, -100 == unsure
        self.atrValue = self.data.atr[0] #Get the atr stoploss value
        if self.order:
            return #If we ordered don't return anything
        if self.rsi_value > 50 and self.candleDir == 1 and self.ema200_value < self.data.close[0] and not self.position and not self.bought_today:
            self.order = self.buy()
            self.bought_today = True
        """
        self.candles_prev += 1 #Go to the next candle

    def stop(self):
        global totalWins, totalLoses, totalStocks, small30PercentLose, small20PercentLose, small10PercentLose, big30Percentwins, big20PercentWins, big10PercentWins
        if self.position:
            print(self.position)

        print(f"FINAL VALUE: {self.broker.getvalue()}")

        if self.broker.getvalue() >= inputCash * 1.3: #30% win
            self.log("*** BIG WINNER ***") #If our portfolio's value is greater than 130,000 (clearly we can change this number or whatever later)
            big30Percentwins += 1
        
        elif self.broker.getvalue() <= inputCash * 0.7: #30% loss 
            self.log("*** MAJOR LOSER ***")
            small30PercentLose += 1
        elif self.broker.getvalue() >= inputCash * 1.2: #20% win
            big20PercentWins += 1
        elif self.broker.getvalue() <= inputCash * 0.8: #20% loss
            small20PercentLose += 1
        elif self.broker.getvalue() >= inputCash * 1.1: #10% win
            big10PercentWins += 1
        elif self.broker.getvalue() <= inputCash * 0.9: #10% loss
            small10PercentLose += 1


        if self.broker.getvalue() > inputCash: #Higher end portfolio val
            totalWins += 1
        if self.broker.getvalue() < inputCash: #Lower end portfolio val
            totalLoses += 1

        totalStocks += 1



            
















if __name__ == '__main__':
    conn = sqlite3.connect(config.dbFile) #Connect to our database
    conn.row_factory = sqlite3.Row #Make conn info indexable objects
    cursor = conn.cursor() #Be able to write to our databse

    #Select distinct stock_id's as stock_id from our appdata databse table called stock_price_minute
    cursor.execute("""
        SELECT DISTINCT(stock_id) as stock_id FROM globalBuySell
    """)

    stocks = cursor.fetchall() #Get all the stocks from there
    # print(stocks['stock_id'])
    symbols = []


    #Select ID from the stocks
    # idOfStockToTest = 1

    # lineForStock = f"SELECT symbol FROM stock WHERE id = {stocksId['stock_id']}"


    # symbols = cursor.execute(lineForStock)

    # stockList = cursor.fetchall()
    # symbols = []
    # for stock in symbols:
    #     symbols.append(stock['symbol'])




    # #stocks = [stocks[0]]
    # #Only run it on the first stock
    
    # stocks = [{'stock_id': idOfStockToTest}]
    

    for stock in stocks:
        # stock = stock['symbol'] #Just get the symbol from it

        cursor.execute("""
            SELECT symbol FROM stock WHERE id = (?)
        """, (stock['stock_id'],))

        currentStock = cursor.fetchone()
        


        print(f"== Testing symbol {currentStock['symbol']} with id {stock['stock_id']} ===")
        
        cerebro = backtrader.Cerebro() #Instantiate backtester
        cerebro.broker.setcash(inputCash) #Give it 1k
        cerebro.addsizer(backtrader.sizers.PercentSizer, percents=95) #Use 10% of our portfolio (don't use 100%)

        cerebro.addstrategy(RsiEmaCandle)

       
        


        #'%H:%M:%S' is hour minute second
        dataframe = pandas.read_sql("""
            SELECT datetime, open, high, low, close, volume, atr, buySellSignals
            from globalBuySell
            where stock_id = :stock_id
            and strftime('%H:%M:%S', datetime) >= '09:30:00'
            and strftime('%H:%M:%S', datetime) < '16:00:00'
            order by datetime asc
        """, conn, params={"stock_id": stock['stock_id']}, index_col='datetime', parse_dates=['datetime'])



        #data = backtrader.feeds.PandasData(dataname=dataframe) #Feed our data as a dataframe
        data = StratData(dataname=dataframe)

        cerebro.adddata(data) #Put the data in the backtrader
        
        #cerebro.addstrategy(RsiEmaCandle) #Specify our strategy here

        cerebro.addanalyzer(backtrader.analyzers.TradeAnalyzer, _name="ta")
        cerebro.addanalyzer(backtrader.analyzers.SQN, _name="sqn")



        #Test our strategy with other parameters to compare (don't overdo this since you might overfit)
        #strats = cerebro.optstrategy(OpeningRangeBreakout, num_opening_bars=[15,30,60])
        strategies = cerebro.run() #Run our strategy
        firstStrat = strategies[0]
        # cerebro.plot() #Can't plot when we're running optstrategy, but otherwise we can plot
        printTradeAnalysis(firstStrat.analyzers.ta.get_analysis())
        printSQN(firstStrat.analyzers.sqn.get_analysis())

        # cerebro.plot() #Can't plot when we're running optstrategy, but otherwise we can plot
        # sys.exit(1)

        # print("\nPerformance:")
        # print(f"Winrate: {totalWins/totalStocks}")
        # print(f"LoseRate: {totalLoses/totalStocks}")
        # print(f"+30% equity chance: {big30Percentwins/totalStocks}")
        # print(f"-30% equity chance: {small30PercentLose/totalStocks}")
        # print(f"+20% equity chance: {big20PercentWins/totalStocks}")
        # print(f"-20% equity chance: {small20PercentLose/totalStocks}")
        # print(f"+10% equity chance: {big10PercentWins/totalStocks}")
        # print(f"-10% equity chance: {small10PercentLose/totalStocks}")
        # sys.exit(1)


        
        




