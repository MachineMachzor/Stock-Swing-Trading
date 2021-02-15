# Stock-Swing-Trading

STRATEGY (subject to review):

Screener: Finviz
- Stock selection: https://ibb.co/DD86CXx AND https://ibb.co/vdttkQL   (Grabs ~180 stocks for evaluation, usually buys 20)


Within script checks:
- Currently above 200ema in the CURRENT day.
- Positive LINEAR REGRESSED slope from 30days ago to today
- Macd crossover upward


Note: Not buying a macd crossover with a PERCENT CHANGE on the CURRENT BAR >= 15% doesn't work.










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


}




WHEN THE SCRIPT IS BEING RUNNED

Task Scheduler OR cronjob to AUTOMATICALLY run the scripts (going to say auto run to refer to this). Used bat files for task scheduler
M-F = Monday through Friday

AUTOMATIC EXECUTION (make sure you did steps 1-3 in normal steps):
1. Set insertTrendingFibvizStocks2 to run M-F at 3:41pm (grabs stocks)
2. Set closePositions to run on Tuesday & Thursday at 3:45pm (Days subject to change) (closes positions).
3. Set macdEmaTrend (called priceActionEma.bat) to run at 3:51pm M-F (reviews grabbed stocks and buys some).








