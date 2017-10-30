This repository contains python (mini) projects. These are to show my level of competance in the python programming langage in the form of an applied program
All code is written in python 3.6

Program 1 : matplotlib_1.py

This code: 

a. reads a URL containing Microsoft stock price data, 

b. extracts end-of-day price data

c. plots data using matplotlib.

Commands used include:

a. urllib.request.urlopen() to read url data, 

b. (i) dateutil.parser() for date info (ii) re.findall() to find floats & integers i.e. price & volume (iii) split() 

These extract relevant data including: date, float & integer types. 

c. matplotlib.pyplot.plot_date to plot the results 



Program 2 : sqlite_database1.py

This code: 

a. creates a small sqlite3 database on used cars i.e. make, model, tupe, age, mileage, price etc. 

b. Allows the user to : Display, Add, Delete & change entries and have a basic search function. 

Commands used include: 

create_connection() & create_connection.cursor(), create_connection.cursor.exectute() 

These create the data base, cursors and execute sqlite3 commands 


Program 3 : Candlestick_1.py

This code builds upon the matplotlib_1.py program above but creates a candlestick graph from Microsoft stock orice data.

It reads/parses/extracts Microsoft stock daily price data (i.e. open price, closing price, low price, high price, volume, date) from the URL and plots this data a candlestock graph.
