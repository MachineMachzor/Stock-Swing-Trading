import sqlite3 
import alpacaConfig as config

#Connect to DBfile
conn = sqlite3.connect(config.dbFile)

#Get the cursor 
cursor = conn.cursor()



cursor.execute("""
    DROP TABLE stock
""")



cursor.execute("""
    DROP TABLE stock_price
""")

cursor.execute("""
    DROP TABLE stock_strategy
""")


cursor.execute("""
    DROP TABLE stock_price_minute_makeothers
""")

cursor.execute("""
    DROP TABLE stock_price_five
""")


cursor.execute("""
    DROP TABLE stock_price_fifteen_newbacktest
""")

cursor.execute("""
    DROP TABLE stock_price_five_crossover
""")

cursor.execute("""
    DROP TABLE lstm_preds
""")

cursor.execute("""
    DROP TABLE trades_tracker
""")

cursor.execute("""
    DROP TABLE rsiStochMacD
""")

cursor.execute("""
    DROP TABLE stdDeviation
""")

cursor.execute("""
    DROP TABLE priceActionEma
""")

cursor.execute("""
    DROP TABLE fisher
""")


cursor.execute("""
    DROP TABLE globalBuySell
""")



#Commit the changes
conn.commit()