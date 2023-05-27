import mplfinance as mpf
from dateutil.relativedelta import relativedelta
import yfinance as yf
from yahoo_fin import stock_info as si
import pandas_market_calendars as mcal
import datetime as dt
import time
import numpy as np
import os

#   Setting the calendar range
start_time = '2023-1-1'
end_time = '2023-12-31'

#   Initialization (You need to give an extra week in the cal so the day generator can work)
nyse = mcal.get_calendar('NYSE')
cal = nyse.schedule(start_date=start_time, end_date=end_time)
a = np.ravel(cal)
dtNyseFormat = []

#   Recreating calendar using datetime.date only
for counter, item in enumerate(a):
    if counter % 2:
        temp2 = str(a[counter]).split('-')
        temp3 = temp2[2].split(' ')
        temp4 = dt.date(int(temp2[0]), int(temp2[1]), int(temp3[0]))
        dtNyseFormat.append(temp4)
    else:
        pass

#   Making sure today is a market day
start = dt.date(2023, 5, 26)  # dt.date.today()
print(start)

#   Instead of this day checker, find "start" in the nyse list, then go -2 in the index and have that be the end date. problem solved!
if start not in dtNyseFormat:
    print("Not a market day! See you next time!")
    quit()

#   Generating days to filter valid days. Increase number of days to have more potential data.
numOfDays = 12
listOfDays = [start + dt.timedelta(days=-numOfDays) for numOfDays in range(numOfDays)]
print(listOfDays)

#   Day Checker
marketDays = []
for day in listOfDays:
    if day in dtNyseFormat:
        marketDays.append(day)
    else:
        pass

#   Edit this value for how many market days you want for the data to be used for the scans
end = marketDays[5]

print(start)
print(end)

startTime = time.time()

#   Ticker list
nasTickers = si.tickers_nasdaq()
dowTickers = si.tickers_dow()

allTickers = nasTickers + dowTickers

# print(allTickers)

outputList6 = []
outputList3 = []

for count, ticker in enumerate(allTickers):
    try:
        print("Progress: ", count, "/", len(allTickers), round(count / len(allTickers), 2) * 100, "%")
        stock_df = yf.download(ticker, end, start)

        #   Dataframe shape checker for preventing duplicate data
        if stock_df.shape[0] >= 2 and stock_df.index[-1] == stock_df.index[-2]:
            stock_df = stock_df[:-1]
        print(stock_df)

        #   Add variables if you add more market days, remove variables if you remove market days

        #   Main Variables (Change variables for your scans)
        o = stock_df.iloc[len(stock_df)-1]['Open']  # First Day, Last in DF (Yesterday)
        o1 = stock_df.iloc[len(stock_df)-2]['Open']
        o2 = stock_df.iloc[len(stock_df)-3]['Open']
        o3 = stock_df.iloc[len(stock_df)-4]['Open']  # Last Day, First in DF

        c = stock_df.iloc[len(stock_df)-1]['Close']
        c1 = stock_df.iloc[len(stock_df)-2]['Close']
        c2 = stock_df.iloc[len(stock_df)-3]['Close']
        c3 = stock_df.iloc[len(stock_df)-4]['Close']

        h = stock_df.iloc[len(stock_df)-1]['High']
        h1 = stock_df.iloc[len(stock_df)-2]['High']

        l = stock_df.iloc[len(stock_df)-3]['Low']
        l1 = stock_df.iloc[len(stock_df)-4]['Low']

        vol = stock_df.iloc[len(stock_df)-1]['Volume']
        vol1 = stock_df.iloc[len(stock_df)-2]['Volume']
        vol2 = stock_df.iloc[len(stock_df)-3]['Volume']
        vol3 = stock_df.iloc[len(stock_df)-4]['Volume']
        vol4 = stock_df.iloc[len(stock_df)-5]['Volume']

        #   Main Filters (Change filters for your scans)
        is4BO = c1 / c2 >= 1.04
        isMoreVol = vol1 > vol2
        isDailyVol = vol >= 500000
        is4DayVol = vol1 > 500000 and vol2 > 100000 and vol3 > 100000 and vol4 > 100000
        is70High = (c1 - l1) * (h1 - l1) >= 0.7
        isDollarMore = c2 - o2 < c1 - o1
        isMoreThanD = c1 > 1.0
        isLessThanD = c1 < 40.0
        isInDollarRange = isMoreThanD and isLessThanD
        isNarrowRange = c2 / o2 < 0.5 and c3 / o3 < 0.5

        isMB3 = is4BO and isMoreVol and isDailyVol and is4DayVol
        isMB6 = is4BO and isMoreVol and isDailyVol and is70High and isDollarMore and is4DayVol

        isPDRed = o2 > c2
        isND4Perc = h / o > 1.04

        #   Conditional Checker
        if isMB6 and isInDollarRange and isND4Perc and isNarrowRange:
            outputList6.append(ticker)
            print(ticker, ": Six Narrow")

        if isMB6 and isInDollarRange and isND4Perc and isPDRed:
            if ticker in outputList6:
                pass
            else:
                outputList6.append(ticker)
                print(ticker, ": Six Red")

        if isMB6 and isInDollarRange and isND4Perc:
            if ticker in outputList6:
                pass
            else:
                outputList6.append(ticker)
                print(ticker, ": Six Norm")

        if isMB3 and isInDollarRange and isND4Perc:
            #   So we don't have duplicates in both lists
            if ticker in outputList6:
                pass
            else:
                outputList3.append(ticker)
                print(ticker, ": Three")

        else:
            print(ticker, ": False")
    except Exception as e:
        print(ticker, e)
        if str(e) == "single positional indexer is out-of-bounds":
            print("Data not updated.")

# STOCK SCREENER
# -----------------------------------------------------------------------
# CHART DOWNLOADER

mc = mpf.make_marketcolors(up='#008542', down='#850000', inherit=True)
s = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc)

end1 = start - relativedelta(months=6)

fileName = str(start) + " 4% ND MB"

os.makedirs(fileName)

outputList6.extend(outputList3)

print(outputList6)

#   Output the list into the file first
with open(fileName + "\\" + str(start) + " Tickers.txt", "w") as f:
    for row in outputList6:
        f.write(row)
        f.write("\n")

for ticker in outputList6:
    try:
        stock = ticker
        filename = fileName + "\\" + stock.lower() + " " + str(start) + ".png"
        stock_df = yf.download(ticker, end1, start)

        if stock_df.shape[0] >= 2 and stock_df.index[-1] == stock_df.index[-2]:
            stock_df = stock_df[:-1]

        mpf.plot(stock_df, type='candle', style=s, volume=True, figratio=(18, 10), figscale=2,
                 tight_layout=True,
                 title=ticker.title(), savefig=filename)
        print(ticker, "downloaded...")
    except Exception as e:
        print(ticker, "Error unknown.", str(e))
        pass

endTime = time.time()
print("Time: ", endTime - startTime)
