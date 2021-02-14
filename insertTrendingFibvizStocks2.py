import requests 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import sys
import sqlite3 
import alpacaConfig as config 
import smtplib, ssl
context = ssl.create_default_context()
from datetime import date 


#Connect to our database
conn = sqlite3.connect(config.dbFile)
conn.row_factory = sqlite3.Row 
cursor = conn.cursor()


#Delete from the stocks list
cursor.execute("""
    DELETE FROM stockGainers
""")

hideChrome = False 
if hideChrome:
    #Make chrome hidden (don't even pop it up), if you wanna see what ur doing just remove the options parameter
    options = webdriver.ChromeOptions()
    options.add_argument("headless")


    #Instantiate driver
    driver = webdriver.Chrome(executable_path=r'D:\chromedriver.exe',
        options=options)
else:
    #Instantiate driver
    driver = webdriver.Chrome(executable_path=r'D:\chromedriver.exe')


#smallCapStocks with high vol
# urlForSmallCapStocks = 'https://finviz.com/screener.ashx?v=111&f=cap_smallover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change&ar=180'
midCapStocks = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change'
midCapStocksPg2 = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change&r=21'
midCapStocksPg3 = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change&r=41'
midCapStocksPg4 = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change&r=61'
midCapStocksPg5 = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change&r=81'
midCapStocksPg6 = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change&r=101'
midCapStocksPg7 = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change&r=121'
midCapStocksPg8 = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change&r=141'
midCapStocksPg9 = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,sh_curvol_o1000,sh_price_o10,ta_averagetruerange_o1,ta_highlow52w_a60h,ta_sma200_pa&ft=4&o=-change&r=161'


fundamentalMidCapIncStocks = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,fa_epsyoy1_o20,fa_salesqoq_u20,ind_stocksonly,ipodate_prev3yrs,sh_avgvol_o500,sh_curvol_o1000,sh_price_o10,ta_changeopen_u,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3&o=-volume'


#Open finvis with the stock filter already set and logged in already
driver.get(fundamentalMidCapIncStocks)

#Just gets the text saying the total number of stocks
getNumOfStocks = int(driver.find_elements_by_xpath("//body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[3]/td[1]/table[1]/tbody[1]/tr[1]/td[1]")[0].get_attribute("innerText").split()[1])
# print(getNumOfStocks)
# sys.exit(1)

def getStocks(link):
    try:
        # global driver #Get our instantiated driver already there
        driver.get(link)

        #Get the number of stocks that is literally stated on the page. ChroPath to get its xpath, and since it has a space, we split() and get the 2nd element
        numInSelection = int(driver.find_elements_by_xpath("//body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[3]/td[1]/table[1]/tbody[1]/tr[1]/td[1]")[0].get_attribute("innerText").split()[1])
        symbols = []
        print(numInSelection)
        for i in range(2, 20+2): #Assuming there's 20 stocks on the page (numInSelection is kinda weird)
            symbols.append(driver.find_elements_by_xpath(f"/html[1]/body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[4]/td[1]/table[1]/tbody[1]/tr[{i}]")[0].get_attribute('innerText').split()[1])
        # driver.quit()
        return symbols
    except:
        return []




symbolsToUse = []
#Scrape the stocks list
if getNumOfStocks <= 20:
    for i in range(2, getNumOfStocks+2):
        symbolsToUse.append(driver.find_elements_by_xpath(f"/html[1]/body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[4]/td[1]/table[1]/tbody[1]/tr[{i}]")[0].get_attribute('innerText').split()[1])
    # driver.find_elements_by_xpath("/html[1]/body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[3]/td[1]/table[1]/tbody[1]/tr[1]/td[5]/a[1]")[0].click() #Go to the next page
    # for i in range(2, 22):
    #     symbolsToUse.append(driver.find_elements_by_xpath(f"/html[1]/body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[4]/td[1]/table[1]/tbody[1]/tr[{i}]")[0].get_attribute('innerText').split()[1])
    # driver.get(midCapStocksPg2)
    symbolsToUse.extend(getStocks(midCapStocks))
    symbolsToUse.extend(getStocks(midCapStocksPg2))
    symbolsToUse.extend(getStocks(midCapStocksPg3))
    symbolsToUse.extend(getStocks(midCapStocksPg4))
    symbolsToUse.extend(getStocks(midCapStocksPg5))
    symbolsToUse.extend(getStocks(midCapStocksPg6))
    symbolsToUse.extend(getStocks(midCapStocksPg7))
    symbolsToUse.extend(getStocks(midCapStocksPg8))
    symbolsToUse.extend(getStocks(midCapStocksPg9))
else:
    #There's just 22 stocks on the first page
    for i in range(2, 22):
        symbolsToUse.append(driver.find_elements_by_xpath(f"/html[1]/body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[4]/td[1]/table[1]/tbody[1]/tr[{i}]")[0].get_attribute('innerText').split()[1])
    # driver.find_elements_by_xpath("/html[1]/body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[3]/td[1]/table[1]/tbody[1]/tr[1]/td[5]/a[1]")[0].click() #Go to the next page
    # for i in range(2, 22):
    #     symbolsToUse.append(driver.find_elements_by_xpath(f"/html[1]/body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[4]/td[1]/table[1]/tbody[1]/tr[{i}]")[0].get_attribute('innerText').split()[1])
    # driver.get(midCapStocksPg2)
    symbolsToUse.extend(getStocks(midCapStocks))
    symbolsToUse.extend(getStocks(midCapStocksPg2))
    symbolsToUse.extend(getStocks(midCapStocksPg3))
    symbolsToUse.extend(getStocks(midCapStocksPg4))
    symbolsToUse.extend(getStocks(midCapStocksPg5))
    symbolsToUse.extend(getStocks(midCapStocksPg6))
    symbolsToUse.extend(getStocks(midCapStocksPg7))
    symbolsToUse.extend(getStocks(midCapStocksPg8))
    symbolsToUse.extend(getStocks(midCapStocksPg9))


    
    # for i in range(2, getNumOfStocks+2):
    #     symbolsToUse.append(driver.find_elements_by_xpath(f"/html[1]/body[1]/table[3]/tbody[1]/tr[4]/td[1]/div[1]/table[1]/tbody[1]/tr[4]/td[1]/table[1]/tbody[1]/tr[{i}]")[0].get_attribute('innerText').split()[1])


# else:
#     with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
#         server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD) #Login
#         email_message = f"Subject: No Stocks to Update: {date.today()}\n\n" #Our email subject
#         server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message) #From, to, message (sending to ourself)
    
#     driver.quit()
#     sys.exit(1)

# print(symbolsToUse)
# sys.exit(1)
#Insert the stocks into the database
for symbol in symbolsToUse:
    cursor.execute("INSERT INTO stockGainers (symbol) VALUES (?)", (symbol,))

print(symbolsToUse)
print(len(symbolsToUse))




conn.commit() #Actually commit to the database



with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD) #Login
    email_message = f"Subject: Updated stocks: {date.today()}\n\n" #Our email subject
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message) #From, to, message (sending to ourself)

# driver.quit() #Close the driver
#Close all windows??
#https://stackoverflow.com/questions/45141407/python-and-selenium-close-all-tabs-without-closing-the-browser
for handle in driver.window_handles:
    driver.switch_to.window(handle)
    driver.close()