"""
Code to read Microsoft stock price data from an URL, extract specific data & plot using
matplotlib

Specific task include 
(i)     reading data from a web page using urllib.request.urlopen(),
(ii)    extracting relevant data including: date, float & integer types, using:
          dateutil.parser() for date info
          re.findall()      to find floats & integers i.e. price & volume
          split()
(iii)   plot the results using matplotlib.pyplot.plot_date
        To experiment in working with the required format of date info
        (numpy.ndarray array), three methods of generating this are tried.

Note - the correct functioning of this code depends on the (i) the URL &
(ii) format of stock data/info from www.alphavantage.com 

"""

import time
import urllib
import re          #re = regular expressions matching options 
import datetime as dt
import matplotlib.pyplot as plt
import dateutil.parser as dparser
import numpy as np

#URL of the Microsoft stock price data
stock_price_url = "http://www.alphavantage.co/query?function=\
TIME_SERIES_DAILY&symbol=MSFT&outputsize=full&apikey=demo"

try:
   #Open stock price date web page & read all the stock data
   source_code = urllib.request.urlopen(stock_price_url).read()\
   .decode("utf-8", "ignore")
except urllib.error.URLError as e1:
    print ("URL error : {}".format(e1))
except urllib.error.HTTPError as e2:
    print ("HTTP or Authentication error : {}".format(e2))
except urllib.error.ContentTooShortError as e3:
    print ("URL content too short : {}".format(e3))
except Exception as e4:
    print ("Error when reading Web data : {}".format(e4))
else:   #read operation was successful
    
    #Split by the newline character
    split_source = source_code.split('\n')

    #Calculate the number of lines in the file
    lines_in_file = len(split_source)

    line_of_first_trade_date = 9  # The first record is known to start at line 9
    lines_at_file_end = 3       # Last three lines are known not to contain data
    lines_per_record = 7        # 7 lines of stock data per day, i.e. 7 lines of data per record
    close_price_offset = 4      # Stock closing price offset within each day of data
    volume_offset = 5           # Stock volume offset within each day of data

    #Caluculate the number of records/days worth of stock
    records_in_file = (lines_in_file - line_of_first_trade_date -\
                       lines_at_file_end +1)//lines_per_record

    trade_dates = []    #Date of trading day
    unix_time_1 = []    # List of days in integer format
    unix_time_2 = []
    close_prices = []   #Closing stock price for each date
    volume_traded = []  #Volume of stocks traded on each date

    record_number = 1

    while record_number <= records_in_file:
        record_start_line = line_of_first_trade_date + \
        (record_number-1)*lines_per_record
        date = dparser.parse(split_source[record_start_line], fuzzy=True)
        trade_dates.append(date)    #trade_date is type datetime.datetime

        #Date type of trade_date.timetuple() is time.struct_time - full 9-tuple
        #Time.mktime produces a float (which is compatible with time())
        unix_time_1.append(int(time.mktime(date.timetuple())))


        #Find & extract the End of Day stock price (type=float) by
        #(i) searching for combination of : <int>+'.'+<int> within the string
        #(ii) converting using string->float &
        #(iii) append/add to the close_price array
        eod_price = re.findall("\d+\.\d+",
                               split_source[record_start_line + close_price_offset])[0]
        close_prices.append(float(eod_price))

        #Stock volume info is contained is in a line of text
        # (i) split the line on the ":" character
        # (ii) use re.findall(),
        # (iii) convert from string->integer &
        # (iv) append/add to the volume_traded array
        list_from_string = split_source[record_start_line + volume_offset].split(':')
        volume = re.findall("\d+", list_from_string[1])[0]
        volume_traded.append(int(volume))

        record_number += 1  #increment the recond number

    # Note Matplotlib.pyplot (below) needs a numpy ndarray containg dates ...
    #... (i.e. x-axis data) to work with matplotlib.pyplot.plot_date
    #Either of 3 methods below that generate the dates work ...
    # (i) using array trade_dates
    # (ii) using numpy.asarray(trade_dates)
    # (iii) convering the array of date interger value unix_time_1 to numpy.ndarray

    #Convert date array to numpy array using numpy.asarray()
    mpl_dates = np.asarray(trade_dates)

    #Run date conversion function to create unix_time_2 of type numpy.ndarray from
    #unix_time_1, a list of integers.
    date_convert = np.vectorize(dt.datetime.fromtimestamp)
    unix_time_2 = date_convert(unix_time_1)

    #Plot the data, labels of x & y axis, title & legend
    plt.plot_date(trade_dates, close_prices, '-', label='MSFT/Microsoft')

    #add gridlines. labels for x & y axes & graph title & show the plot/graph
    plt.grid(True, color='y', linestyle='-', linewidth=1)
    plt.xlabel('Date')
    plt.ylabel('$')
    plt.title('Stock prices')
    plt.legend()
    plt.show()
