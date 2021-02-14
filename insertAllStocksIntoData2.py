import sqlite3
import alpacaConfig as config 
from selenium.webdriver.common.keys import Keys
from selenium import webdriver 



conn = sqlite3.connect(config.dbFile) 
conn.row_factory = sqlite3.Row #Make the printed stuff objects

cursor = conn.cursor()

#How to insert correct values into each row
#cursor.execute("INSERT INTO STOCK (symbol, name, exchange, shortable) VALUES ('ADBE', 'Adobe Inc.', 'NASDQ', 'True')")



import sys 
import alpaca_trade_api as tradeapi 

#Initialize the alpaca trade api
api = tradeapi.REST(config.apiKey, config.secretKey, base_url=config.baseUrl)

#Get the assets, such as the symbol, exchange, name, and if it's shortable
assets = api.list_assets()

# assets.symbol, assets.status, assets.name


#Selects the symbol and name from each stock
cursor.execute("""
    SELECT symbol, name FROM stock
""")

rows = cursor.fetchall()



# #FROM previous run (if this program was run prior) just make this list to not add duplicates
symbolsPreviously = [row['symbol'] for row in rows]





# driver = webdriver.Chrome(executable_path=r"D:\chromedriver.exe"); #Path of your webdriver chromedriver, which you install with the link above

# #Maximize the window
# driver.set_window_position(1024, 600) 
# driver.maximize_window()

# url = "https://www.fool.com/premium/screener/?convictions=Positive#scorecard-filters"


# driver.get(url)
# #Waits for an element to be found (Means it doesn't necessarily wait 30 seconds)
# driver.implicitly_wait(30) 

# inputUser = driver.find_elements_by_xpath("/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/form[1]/div[2]/input[1]")[0].send_keys(config.MOTLEY_EMAIL)
# inputPass = driver.find_elements_by_xpath("/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/form[1]/div[3]/input[1]")[0].send_keys(config.MOTLEY_PASS)
# pressSubmit = driver.find_elements_by_xpath("/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/form[1]/button[1]")[0].click()

# #Waits for an element to be found
# driver.implicitly_wait(30)

# #Find where it says positive only then click (this was taken from ChroPath as such all other paths)
# positiveOnly = driver.find_elements_by_xpath("//a[contains(text(),'Positive Only')]")[0].click()
# assetClassLarge = driver.find_elements_by_xpath("//body/div[@id='page-container']/section[@id='content']/section[@id='main-content']/div[1]/main[1]/div[1]/div[2]/section[1]/div[4]/ul[1]/li[3]/label[1]/input[1]")[0].click()

# #Make it sort by prices by clicking the sort thing twice
# for i in range(2):
#     priceSort = driver.find_elements_by_xpath("/html[1]/body[1]/div[1]/section[1]/section[3]/div[1]/main[1]/div[1]/div[2]/div[1]/div[1]/div[3]/table[1]/thead[1]/tr[1]/th[5]/div[1]/span[1]")[0].click()


# #Waits for an element to be found (not actually waiting 30 seconds)
# driver.implicitly_wait(30)


# #Get the table of everything (returns a big string body of the table)
# fullTable = driver.find_elements_by_xpath("/html[1]/body[1]/div[1]/section[1]/section[3]/div[1]/main[1]/div[1]/div[2]/div[1]/div[1]/div[3]/table[1]/tbody[1]")[0].get_attribute("innerText")

# #print(fullTable)
# fullTable = fullTable.split("\n") #Split it by every endline break
# symbolsToUse = [] #This is new symbols to add (these are only symbols that have a positive incline)




# n = 0
# for table in fullTable:

#     #print(table)
#     #Always use this kinda method to debug stuff (if you don't you'll be confused)
#     #print(f"############################################# -> n = {n}")
    
#     if n == 0: #Indicates that the first line (element) has a line with a symbol. Uncomment the print lines above
#         table = table.split() #Splits a string with just whitespace
#         print(table)
#         table = table[-4] #Gets the 4th element back from the last (the symbol) -> this is consistent
#         print(table) 

#         symbolsToUse.append(table)
    
#     n += 1
#     if n >= 6: #Reset it (this kinda was guessed, but FOR SURE use the debugging method commented out before)
#         n = 0
    
# print(symbolsToUse)


easyToBorrowOnly = False

if easyToBorrowOnly == True:
    for asset in assets:
        try:
            #This way we don't have duplicates (this was debugged)
            #Asset should also be easy to borrow
            if asset.status == 'active' and asset.tradable and asset.symbol not in symbolsPreviously and asset.easy_to_borrow:
                print(f"Added a new stock {asset.symbol} {asset.name}")
                cursor.execute("INSERT INTO STOCK (symbol, name, exchange, shortable) VALUES (?, ?, ?, ?)", (asset.symbol, asset.name, asset.exchange, asset.shortable))
        except Exception as e:
            print(asset.symbol) #Symbol that was the duplicate
            print(e) #Prints the exception
else:
    for asset in assets: #Just use every symbol regardless
        try:
            #This way we don't have duplicates (this was debugged)
            #Asset should also be easy to borrow
            if asset.status == 'active' and asset.tradable and asset.symbol not in symbolsPreviously:
                print(f"Added a new stock {asset.symbol} {asset.name}")
                cursor.execute("INSERT INTO STOCK (symbol, name, exchange, shortable) VALUES (?, ?, ?, ?)", (asset.symbol, asset.name, asset.exchange, asset.shortable))
        except Exception as e:
            print(asset.symbol) #Symbol that was the duplicate
            print(e) #Prints the exception








conn.commit()
print("Done")