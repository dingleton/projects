# -*- coding: utf-8 -*-
"""
Program to 
a. Access web page containing Microsoft daily stock price data
b. Parse the data to extract (i) date (ii) open price, (iii) high price
   (iv) low_oprice, (v) close price (vi) volume of stock traded
c. Plot this on a candlestick graph
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates     #Matplotlib date convertor
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc
from matplotlib.finance import candlestick2_ohlc

import dateutil.parser as dparser
import urllib
import re


#url of Microsoft stock price data
stock_price_url = "http://www.alphavantage.co/query?function=\
TIME_SERIES_DAILY&symbol=MSFT&outputsize=full&apikey=demo"

#Read url code
source_code = urllib.request.urlopen(stock_price_url).read().decode("utf-8", "ignore")

#Note - the equivalent outcome but split into 3 statements is :
# 1. response = urllib.request.urlopen(stock_price_url)
# 2. data = response.read()      # a `bytes` object
# 3. source_code = data.decode("utf-8", "ignore") # a `str`; this step can't be used if data is binary
# Python3 does not read the html code as a string but as a bytearray ...
#... so you need to convert it to one with decode.



#Split the lines on the newline character
split_source = source_code.split('\n')

lines_in_file = len(split_source)

#Format of the url has lines at start and end that do not contain ...
#... price data.
#Individual records (i.e. stock price info for one day) are ...
#... contained in a number of lines
lines_at_start = 9
lines_at_end = 3
lines_per_record = 7

#initialise the lists that will hold data
trade_date, open_price, high_price = [], [], []
low_price, close_price, volume_traded = [], [], []
ohlc_data, ohlc_data_2 = [], []

#Read through each line in the url data and extract data & append it to list
#Note - reformatting of data is needed to be acceptable to matplotlob
line_num = 1
for line in split_source:
    if line_num >= (lines_in_file - lines_at_end + 1):
        #Avoid Value errors by *not* reading the final lines of the file.
        break
    elif line_num > lines_at_start:
        #Avoid reading the lines at the start
        if line_num % lines_per_record == 3:
            t_date = dparser.parse(line, fuzzy=True)
            trade_date.append(mdates.date2num(t_date))
            #Convert from datetime -> matplotlib dates & append to list
        elif line_num % lines_per_record == 4:
            o_price = re.findall("\d+\.\d+", line)[0]
            open_price.append(np.float64(o_price))
            #Convert to numply.float64 format & append to list
        elif line_num % lines_per_record == 5:
            h_price = re.findall("\d+\.\d+", line)[0]
            high_price.append(np.float64(h_price))
            #Convert to numply.float64 format & append to list
        elif line_num % lines_per_record == 6:
            l_price = re.findall("\d+\.\d+", line)[0]
            low_price.append(np.float64(l_price))
            #Convert to numply.float64 format & append to list
        elif line_num % lines_per_record == 0:
            eod_price = re.findall("\d+\.\d+", line)[0]
            close_price.append(np.float64(eod_price))
            #Convert to numply.float64 format & append to list
        elif line_num % lines_per_record == 1:
            #Split the line with the volume info on the ':' character
            list_from_string = line.split(':')
            #Now find the multi digit integer from the text
            volume = re.findall("\d+", list_from_string[1])[0]
            volume_traded.append(int(volume))
            #Convert to an integter & append to list
    line_num += 1

#Check the data on price (open, close, high, low), volume-traded and dates
#.... are all the same length, otherwise raise an exception
count = 0
all_data = [trade_date, open_price, high_price, low_price, close_price, volume_traded]
count_max = len(trade_date)

if all(len(x) == count_max for x in all_data):
    pass
else:
    print("Error - Arrays of price(s), volume or date data must be the same length\n\
          Check the data source")
    raise(Exception)
    

#Create a list of tuples where each tuple contains ; 
#... date, open_price, high_price, low_price, close_price & volume_traded
ohlc_data = []
while count < count_max:
    one_day_of_data = trade_date[count], open_price[count], high_price[count], \
    low_price[count], close_price[count], volume_traded[count]
    ohlc_data.append(one_day_of_data)
    count+=1

fig, ax = plt.subplots()

#Create/draw candlestick graph.
#Note candlestick_ohlc needs data in tuple format (not a list). 
candlestick_ohlc(ax, tuple(ohlc_data))

#Note - a Second function to display stock data  has been tried 
# .. and works but is commented out
#candlestick2_ohlc(ax, open_price, high_price, low_price, close_price, width = 0.75)

xdate = trade_date

ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
ax.xaxis.set_major_locator(mticker.MaxNLocator(10))
ax.grid(True)

fig.autofmt_xdate() #This should avoid any overlap in date on x axis
fig.tight_layout()

#Set the low/high limit on the Y axis to be 0 & 15% higher than ...
#... maximum value of high_price
ax.set_ylim(0, max(high_price)*1.15)

#Alternative way to rotate date by 45 degrees to avoid overlapping text.
#for label in ax.xaxis.get_ticklabels():
#    label.set_rotation(45)

plt.xlabel('Date')
plt.ylabel('Stock Price $')
plt.title('Microsoft MSFT')
plt.legend()

plt.show()
