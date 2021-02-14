import sqlite3
import alpacaConfig as config

#Connect to dbfile
conn = sqlite3.connect(config.dbFile)

#Gte the cursor for writing
cursor = conn.cursor()

#delete
cursor.execute("""
    DELETE FROM priceActionEma
""")

cursor.execute("""
    DELETE FROM fisher
""")

cursor.execute("""
    DELETE FROM globalBuySell
""")

conn.commit()