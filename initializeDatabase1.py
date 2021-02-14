import sqlite3 
import alpacaConfig as config 
 
#connect to the database
connection = sqlite3.connect(config.dbFile)

cursor = connection.cursor()


#Creates a stock table. Id is the id associated with each stock
#shortable is a boolean since a stock can either be shortable or not shortable
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        name TEXT NOT NULL,
        exchange TEXT NOT NULL,
        shortable BOOLEAN NOT NULL
    )
""")


#Pick the strategy you want
cursor.execute("""
    CREATE TABLE IF NOT EXISTS strategy (
        id INTEGER PRIMARY KEY,
        name NOT NULL
    )
""")




#FOREIGN KEY (stock_id) REFERENCES stock (id) matches every instance of a stock_id to be it's cooresponding stock
#https://ibb.co/XL7Lrzk 
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        date NOT NULL,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        avgVolume20 NOT NULL,
        latestVwap NOT NULL,
        sma_20,
        sma_50,
        rsi_14,
        atr,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")

#Put in a strategy
#Coorespond stock_id with the same unique stock, and strategy_id matches the stock you want to add the strategy for
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_strategy (
        stock_id INTEGER NOT NULL,
        strategy_id INTEGER NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
        FOREIGN KEY (strategy_id) REFERENCES strategy (id)
    )
""")


#For historical data backtrading
#candlestickPatternDir = candlestick pattern direction (go to script named rsiEmaCandlestickStrat4.py for this)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price_fifteen (
	 id INTEGER PRIMARY KEY,
	 stock_id INTEGER,
	 datetime NOT NULL,
	 open NOT NULL,
	 high NOT NULL,
	 low NOT NULL,
	 close NOT NULL,
	 volume NOT NULL,
     avgVolume, 
     vwma20,
     sma20,
     atr,
     vwap,
	 FOREIGN KEY (stock_id) REFERENCES stock (id)
	)
""")


#Use this to make the other timeframes
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price_minute_makeothers (
	 id INTEGER PRIMARY KEY,
	 stock_id INTEGER,
	 datetime NOT NULL,
	 open NOT NULL,
	 high NOT NULL,
	 low NOT NULL,
	 close NOT NULL,
	 volume NOT NULL,
     avgVolume, 
     vwma20,
     sma20,
     atr,
     vwap,
	 FOREIGN KEY (stock_id) REFERENCES stock (id)
	)
""")



#5min crossover
#Note: both cross_up and cross_down just indicate when it crosses over EITHER OR BOTH senkou_span_a and senkou_span_b (the upper and lower limits of the ichimoku cloud) so we need to see if the close is above the highest span to see if it crossed up, or below the lowest
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price_five_crossover (
	 id INTEGER PRIMARY KEY,
	 stock_id INTEGER,
	 datetime NOT NULL,
	 open NOT NULL,
	 high NOT NULL,
	 low NOT NULL,
	 close NOT NULL,
	 volume NOT NULL,
     avgVolume, 
     senkou_span_a,
     senkou_span_b,
     tenkan_sen,
     kijun_sen,
     senkou_cross_up,
     senkou_cross_down,
     hammerCandles,
     breakawayBullish,
     tekanKijunCross,
     atr,
     vwap,
	 FOREIGN KEY (stock_id) REFERENCES stock (id)
	)
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS ichimoku_swimg_trading (
	 id INTEGER PRIMARY KEY,
	 stock_id INTEGER,
	 datetime NOT NULL,
	 open NOT NULL,
	 high NOT NULL,
	 low NOT NULL,
	 close NOT NULL,
	 volume NOT NULL,
     senkou_span_a,
     senkou_span_b,
     tenkan_sen,
     kijun_sen,
     atr,
     tekanKijunCross,
     crossedCloud,
	 FOREIGN KEY (stock_id) REFERENCES stock (id)
	)
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price_fifteen_newbacktest (
	 id INTEGER PRIMARY KEY,
	 stock_id INTEGER,
	 datetime NOT NULL,
	 Open NOT NULL,
	 High NOT NULL,
	 Low NOT NULL,
	 Close NOT NULL,
	 Volume NOT NULL,
	 FOREIGN KEY (stock_id) REFERENCES stock (id)
	)
""")




#Create a replica of stock_price_minute except it's for 5mins instead of 15mins
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price_five (
      id INTEGER PRIMARY KEY,
      stock_id INTEGER,
      datetime INTEGER,
      open NOT NULL,
      high NOT NULL,
      low NOT NULL,
      close NOT NULL,
      volume NOT NULL,
      avgVolume,
      vwma20,
      sma20,
      atr,
      vwap,
      FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")


#Will just keep track of the daytrades (one complete buy and sell)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS three_day_trades (
      threeDayTrades
    )
""")


#I'll try to implement each strategy taking into consideration both the bullish and bearish traits
#Implementing this first
strategies = ['bollinger_bands', 'ichimoku']
for strategy in strategies:
    cursor.execute("""
        INSERT INTO strategy (name) VALUES (?)
    """, (strategy,))


#Create a replica of stock_price_minute except it's for 5mins instead of 15mins
cursor.execute("""
    CREATE TABLE IF NOT EXISTS lstm_preds (
      id INTEGER PRIMARY KEY,
      stock_id INTEGER,
      datetime INTEGER,
      open NOT NULL,
      high NOT NULL,
      low NOT NULL,
      close NOT NULL,
      volume NOT NULL,
      avgVolume,
      vwma20,
      sma20,
      atr,
      lstmPreds,
      vwap,
      FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")

#Keeps track of stocks we BOUGHT AND SOLD by the bot (not us), plus it keeps track of daytrades
cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades_tracker (
      symbol TEXT NOT NULL,
      datetime INTEGER,
      buyOrSell NOT NULL,
      qty NOT NULL,
      dayTrades
      )
""")


#Our rsi stoch macd strategy
cursor.execute("""
    CREATE TABLE IF NOT EXISTS rsiStochMacD (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        datetime INTEGER,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        rsi,
        macd_buysell,
        stochP,
        stochK,
        atr,
        stockPKSignals,
        stochCrossoverImplications,
        macDCriteriaBuySells,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS priceActionEma (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        datetime INTEGER,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        dojis,
        breakouts,
        emasCrossing,
        emasSameDir,
        emasGeneralTrend,
        aboveAvgVolume,
        candleBullOrBear,
        atr,
        buySellSignals,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")


#Just make buy sell signals within the actual program, and just call this database honestly (too much work making a shit ton of databases, and we want to be able to quickly implement strats)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS globalBuySell (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        datetime INTEGER,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        atr,
        buySellSignals,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")


#Our rsi stoch macd strategy
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stdDeviation (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        datetime INTEGER,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        stdDev,
        cmf,
        atr,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS fisher (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        datetime INTEGER,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        dojis,
        breakouts,
        emasCrossing,
        emasSameDir,
        emasGeneralTrend,
        aboveAvgVolume,
        candleBullOrBear,
        atr,
        fisher,
        fisherSignals,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")

#This is just for a symbol list of top gainers from finvis
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stockGainers (
        symbol NOT NULL
    )
""")




#Commit the changes to the database
connection.commit()


