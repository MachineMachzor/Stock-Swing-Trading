# Stock-Swing-Trading

STRATEGY (subject to review):
{

Screener: Finviz
1. Stock selection: https://ibb.co/DD86CXx AND https://ibb.co/vdttkQL   (Grabs ~180 stocks for further evaluation specified below)


Within script checks (Note:
2. Currently above 200ema in the CURRENT day.
3. Positive LINEAR REGRESSED slope from 30 days ago
4. Macd crossover upward


Note: Not buying a macd crossover with a PERCENT CHANGE on the CURRENT BAR >= 15% doesn't work.


}







REGARDING RUNNING THE APPLICATION:
{

Runs on SQLITE3 database (go to respitory Stock-Algotrading-NewstNImproved just to learn how to set one up from scratch)


MANUAL EXECUTION:
1. Configure alpacaConfig (set paper/real trading, add email, pass, sqite3 database location etc). Don't need motley account
2. Run initializeDatabase1
3. Run insertStocks2
4. Run insertTrendingFibvizStocks2 stocks
5. Run macdEmaTrend (go to Inputs and configure it. Ignore pdtRule it's swing trading)
6. Run closePositions to close your positions


Task Scheduler OR cronjob to AUTOMATICALLY run the scripts (going to say auto run to refer to this). Used bat files for task scheduler
M-F = Monday through Friday

AUTOMATIC EXECUTION (make sure you did steps 1-3 in normal steps):
1. Set insertTrendingFibvizStocks2 to run M-F at 3:41pm
2. Set closePositions to run on Tuesday & Thursday at 3:45pm (Subject to change)
3. Set macdEmaTrend (called priceActionEma.bat) to run at 3:51pm M-F.


}





