# -*- coding: utf-8 -*-
"""
Python code to test/experiment with code to create a sqlite3 database

Code adds an initial stock of used cars to a sqlite3 database then allows the
user option to : Display the database,  Add, Delete, or  Change entries and
a simple search function

Please note this code was writted to demonstrate a level of competance in
sqlite3 & Python. Many enhancements are possible, especially of the user interface

Notes on the structure of the code
1. Functions are used for code that is used multiple times or has a "standone"
functionality that can be partitioned with no loss of code readibility
2. Some Global variables are used in the functions including : (i) cursor &
(ii) tuples ofinfo on the database columns : column_names, column_types,
column_defaults, column_justify & column_min_max (iii) Database table name

Code written & tested in Python 3.6
"""

import sqlite3 as sql3
from sqlite3 import Error
import datetime

def construct_command(*args):
    """
    Function to accept a variable number of strings that make up a
    partial sqlite3 search command and return them in a concatenated string
    Input parameters : *args, a list of stings
    Output parameters : the concatenated string
    """
    partial_command = ""
    for element in args:
        partial_command += element
    return partial_command


def create_table():
    """
    Function to create a table in a database with used car data.

    Originally the database column names etc were 'hard wired'
    This construction was created to make is easier to cope with a change of
    Daytabase name.
    Note - I do not know if this form of sqlite3 command construction is
    considered safe or prone to injection errors

    Input parameters: None

    Global Parameters used
    a. column_names - tuple of strings/Database column names
    b. column_types - tuple of strings/Type of data for each column
    c. column_defaults - tuple of strings/Default values for each column
    d. car_table - text/Database table name.
    Return Paramters : None
    """
    try:
        command = construct_command('CREATE TABLE IF NOT EXISTS ', car_table, ' ')
        #Add the column names, types of data & default values.
        for col_num, col_name in enumerate(column_names):
            if col_num == 0:
                command += construct_command('(', col_name.lower(), ' ',
                                             column_types[col_num].upper(), ' ',
                                             'PRIMARY KEY UNIQUE')
            else:
                command += construct_command(', ', col_name.lower(), ' ',
                                             column_types[col_num].upper())
                #Add default data text only if specified - this must cope with
                #... both INTEGER & TEXT data
                if len(column_defaults[col_num]) > 0:
                    command += construct_command(' DEFAULT ',
                                                 column_defaults[col_num].upper())
                #Add the final close bracket ')'
            if col_num == len(column_names) - 1:
                command += (')')
        c.execute(command)

    except Error as err:
        print("Error when creating table {}\n{}".format(car_table, err))


def add_cars(car_records):
    """
    Function to enter new records into the database table
    Input parameters:
    1. car_records - a list of tuples that contain data on each car
    Return Parameters : None
    Global variables used : car_table/name database table
    This will work with one or more tuples of data
    """
    try:
        with conn:
            c.executemany("INSERT OR IGNORE INTO " + car_table + \
                      "(id, make, model, type, year, mileage, price) \
                      VALUES (?, ?, ?, ?, ?, ?, ? )", car_records)
    except Error as err:
        print("Error : Entry was not written to DataBase, check ID is unique\n{}\n{}\n"
              .format(car_records, err))
    #Notes
    #1. This construction of the INSERT statement is more secure and avoids.
    #..potential injection errors from rogue strings
    #2. However, I'm not sure if passing "table_name" is secure as
    # most tutorial examples have the table name "hard wired"
    #3. car_record data must be a tuple, even if it only has one value e.g ('xxxx',)
    #4. Connection object is used as a context manager which automatically
    # commits the data (unless these is an exception)
    #5. when constructing SQL command, parameter markers can be used only
    #for expressions, i.e., values. They cannot be used for identifiers like ...
    #...table and column names.
    #see https://stackoverflow.com/questions/13880786/python-sqlite3-string-variable-in-execute
    #6. This comment applies for all functions where the database table name is
    #passed as an input parameter.
    #Should the table name change, this will make the code more maintainable.



def delete_car(car):
    """
    Function to delete a database record from the specified database table
    Input Parameters:
    1. car - integer/database record ID to be deleted &
    Return parameters: None
    Global Parameters used : car_table - text/name of database table
    """
    try:
        with conn:
            conn.execute("DELETE from " + car_table + " where ID = ?", (car,))
    except Error as err:
        print("Error : Entry could not be deleted from to DataBase, check ID : {} is valid\n{}"
              .format(car, err))


def create_connection(db_file):
    """
    Function to create a connection to a sqlite3 database
    Input Parameters : text/name of database file
    Return Parameters : connection or None in the case of failure/Exception
    """
    #Create a connection & cursor
    #sqlite3.connect() will create a file if none exists
    try:
        local_conn = sql3.connect(db_file)
        return local_conn
    except Error as err:
        print("Error in connecting to {}\n{}".format(db_file, err))
    return None


def change_entry(row, column_name, new_entry):
    """
    Function to change one column for one database entry
    Input Paramaters
    1. id - integer/ID of database entry
    2. column_name - text/name of column
    3. new_entry - text/new data for column
    Return parameters - None
    """
    try:
        with conn:
            conn.execute("UPDATE " + car_table + " set " + column_name +
                         " = ? where ID = ?", (new_entry, row))
            conn.commit()
    except Error as err:
        print("Error when trying to change ID {}, column {} to value {}\n{}"
              .format(row, column_name, new_entry, err))


def find_in_db(search_data):
    """
    This function selects cars from  the database and selects cars in specified
    table with the specified "search_data".
    It first build up the database query string from the parameters given in
    the input tuple "search_data" before executing the command.
    Input Paramaters
    1. search_data -tuple with two entries on search data, one for text &
       integer based queries
    Global variables used : car_table/name database table, Cursor
    Return parameters - None, but it does change the global cursor variable
    c (create_connection.cursor()).
    """

    #Define the common text at the start and end of the command string
    command = construct_command("SELECT * FROM ", car_table, " WHERE")

    count = 0
    for key, value in search_data[0].items():
        #search_data[0] contains the criteria for searching the columns with
        # text data
        # Search term "LIKE" is used => the search is case *insensitive*
        if count == 0:
            command += construct_command(" ", key, " LIKE '", value, "'")
        else:
            command += construct_command(" and ", key, " LIKE '", value, "'")
        #Add the text " and " only for second and subsequant search criteria
        count += 1

    for key, value in search_data[1].items():
        #search_data[1] contains the criteria for searching the columns with
        # integer data
        #Note - error checking, including if max > min value should be done
        #.. by the calling function.
        if count == 0:
            command += construct_command(" ", key, " BETWEEN ", str(value[0]),
                                         " AND ", str(value[1]))
        else:
            command += construct_command(" and ", key, " BETWEEN ", str(value[0]),
                                         " AND ", str(value[1]))
        #Add the text " and " only for second and subsequant search criteria
        count += 1

    if count != 0:
        try:
            with conn:
                c.execute(command)
        except Error as err:
            print("Error when trying to find entries in database {}\nCommand line {}\n"
                  .format(err, command))
    else:
        # Search parameters were empty
        print("Error - No search parameters given\n")


def print_cursor_data(title, local_cursor):
    """
    Function to print the data selected by the cursor
    This will print all columns or each row selected by the cursor.
    Input parameters:
    1. title - text, title printed before the database values
    2. local-Cursor - cursor
    Global variables used
    1. column_names, column_types, column_justify - tuples of info on the
    column names, types, widths(used when right justifying text) etc.
    """
    print(title)
    num_columns = len(column_names)
    num_rows = 0

    #Print the column names
    #The right justification value is in the tuple column_justify..
    #.. which has global scope
    row_text = ""
    for col in range(num_columns):
        row_text += column_names[col].rjust(column_justify[col])
    print(row_text)

    #Now print database values for each row
    for row in local_cursor.fetchall():
        row_text = ""
        for item in range(num_columns):
            if column_types[item] == "INTEGER":
                row_text += repr(row[item]).rjust(column_justify[item])
            else:
                if column_types[item] == "TEXT":
                    row_text += row[item].rjust(column_justify[item])
        print(row_text)
        num_rows += 1

    if num_rows == 0:
        print("No data found")


def print_entire_db(message):
    """
    Function to select and print the entire database
    Input parameters
    1. text - a header message to be printed
    Global variables used : c/Cursor
    Output paramters : None (but it will print the database!)
    """
    c.execute("SELECT * FROM " + car_table)
    print_cursor_data(message, c)


def input_integer(msg_prompt, min_value=0, max_value=0):
    """
    Function to prompt for & return an integer value.
    If max > 0, the integer will be checked it is in range min <= integer <= max
    Input paramaters
    msg_prompt : text/message used to prompt user for input
    min_value, max_value : integers/Minimum & maximum value
    Output parameters : integer value
    """
    while True:
        response = input(msg_prompt + " > ")
        try:
            int_response = int(response)
            #only check if value is between min and max if max <= 0
            if max_value > 0:
                if min_value <= int_response <= max_value:
                    return int_response
                else:
                    print("Error, number must be between {} and {}"
                          .format(min_value, max_value))
            else:
                return int_response
        except ValueError:
            print("Error - Input {} is not an integer".format(response))


def input_min_max_int(col_num):
    """
    Function to prompt user for a pair of min & max integer values
    Input parameters : col_num/integer - database column number
    Output parameters : tuple of two integers (min number, max number)
    Global parameters used : column_names & column_min_max
    """
    min_max = []
    min_max.append(input_integer("Input max " + column_names[col_num],
                                 column_min_max[col_num][0],
                                 column_min_max[col_num][1]))
    min_max.append(input_integer("Input min " + column_names[col_num],
                                 column_min_max[col_num][0],
                                 column_min_max[col_num][1]))
    return (min(min_max), max(min_max))


def input_text_capitalized(prompt_name):
    """
    Function to prompt user for a name/text sytring and return the capitalized
    version of the string
    """
    text_data = str(input("Input " + prompt_name + " > "))
    return text_data.capitalize()


def input_text(prompt_name, max_chars=0):
    """
    Function to prompt for & return string input
    Input parameters : prompt/text & mac_chars/Integer = max length of string
    Return Paramters : text inputted by user, truncated to max_chars in length
    """
    text_data = str(input("Input " + prompt_name + " > "))
    #check if text string is too long & truncate if necessary
    if (max_chars > 0) and len(text_data) > max_chars :
        text_data = text_data[:max_chars]
    return text_data


def menu_options():
    """
    Function to display menu options & prompt for a valid selection
    Return Parameters : Integer of selected option
    """
    print("\nOptions :")
    print("1. Display entire database")
    print("2. Add a new entry")
    print("3. Change an entry")
    print("4. Delete an entry")
    print("5. Search database")
    print("0. Exit")
    local_choice = input_integer("Choose option", 0, 5)
    return local_choice

def enter_car_info():
    """
    Function to prompt user to enter data on car.
    Integer values are checked again min & max values
    Input parameters : None
    Global variables used : column_min_max
    Output Parameters : tuple of info on the car with car ID number set to None
    """
    make = input_text("Make", column_justify[1]-1)
    model = input_text("Model", column_justify[2]-1)
    c_type = input_text("Type", column_justify[3]-1).capitalize()
    year = input_integer("Year (4 digit format)", column_min_max[4][0], column_min_max[4][1])
    mileage = input_integer("Mileage", column_min_max[5][0], column_min_max[5][1])
    price = input_integer("Price", column_min_max[6][0], column_min_max[6][1])

    return(None, make, model, c_type, year, mileage, price)

def enter_column_number(local_prompt, display_options):
    """
    Function to
    1 - print the column numbers & names (if display_option == True)
    2 - enter a valid column number

    Input parameters:
    1. prompt - Text. Text displayed when prompting for a response
    2. display_options - Boolean, if True the column name and numbers will be displayed
    Return paramaters : Integer - column number entered by user
    Global variables used: column_names
    """
    num_columns = len(column_names)
    if display_options:
        print("Column numbers & names")
        for col in range(1, num_columns):
            print("{} : {},  ".format(col, column_names[col]), end="")
            if col == num_columns:
                print("\n")
    return input_integer(local_prompt, 1, num_columns)

#End of function definitions

#Start of main body of code

#Define sql3_file, the database file
#sql3_file = ':memory:'          #Used as an alternative to disk file
sql3_file = 'used_car_stock.db'  #Used as an alternative to ':memory:'

#Define sql3 database table name
car_table = 'cars_for_sale'


#Define tuples of data for each database column (i) name, (ii) type of Data
#(iii) Default values, (iv) number of spaced used to right justify when printing
#and minimum & maximum allowable values - note these ese are only specified ..
#.. for INTEGER data types
#NOTE - these global variables are accesed by many of the functions defined above
column_names = ("ID", "Make", "Model", "Type", "Year", "Mileage", "Price")
column_types = ("INTEGER", "TEXT", "TEXT", "TEXT", "INTEGER", "INTEGER", "INTEGER")
column_defaults = ("", "", "", "", "0", "0", "0")
column_justify = (5, 10, 10, 12, 7, 10, 8)

# Set minimum & maximum values for integer types.
# Price & mileage are both set to 0 (min) & 250000 (max).
# Year is set to a min of 1970 & maximum of the curent year
column_min_max = ((), (), (), (), (1970, datetime.datetime.now().year),
                  (0, 250000), (0, 250000))


#Define initial stock of cars - three different method are used (...
#... this is to practise using different command structures.
initial_stock_1 = [(1, 'Ford', 'Focus', 'Hatchback', 2011, 45900, 4000),
                   (2, 'Ford', 'Focus', 'Estate', 2014, 32000, 7000),
                   (3, 'Ford', 'Fiesta', 'Hatchback', 2016, 19750, 6000),
                   (4, 'Fiat', '500', 'Saloon', 2013, 37000, 5900),
                   (5, 'Skoda', 'Fabia', 'Estate', 2014, 32000, 7200)]

#Define more cars, note ID number is set to None - sql3lite should ...
#... automatically choose the next highest number
initial_stock_2 = (6, 'Ford', 'Mondeo', 'Hatchback', 2010, 100000, 3750)
initial_stock_3 = (7, 'Citroen', 'C2', 'Hatchback', 2015, 10500, 8200)
initial_stock_4 = (8, 'Honda', 'Civic', 'Cabriolet', 2014, 45000, 6500)


#Create a connection to a new database
conn = create_connection(sql3_file)

#create a cursor element
c = conn.cursor()

#Call function to create the table.
create_table()

#Populate the table with initial_stock_1 of cars
add_cars(initial_stock_1)

#Add two new cars to the table in the database
#Use .extend method to add two tuples of data
more_cars = []
more_cars.extend((initial_stock_2, initial_stock_3, initial_stock_4))
#Add these to the database with add_cars() function
add_cars(more_cars)

print_entire_db("Database after inserting inital stock of cars")

while True:
    choice = menu_options()
    if choice == 0:
        #exit from program
        break
    elif choice == 1:
        #print entire database option
        print_entire_db("Car Database")
    elif choice == 2:
        #add a new database entry
        new_cars = enter_car_info()
        add_cars([new_cars])
        print_entire_db("Database with new car added")
    elif choice == 3:
        #change a database entry
        change_id = input_integer("Enter car ID number to be changed")

        find_in_db(({'ID':str(change_id)}, {}))    #Search database for ID number
        record_exists = c.fetchone()
        if record_exists is None:
            print("Invalid ID number {}".format(change_id))
        else:
            change_column = enter_column_number("Enter column name to be changed", True)
            prompt = "Enter new value for " + column_names[change_column]
            if column_types[change_column] == 'INTEGER':
                new_int = input_integer(prompt, column_min_max[change_column][0],
                                        column_min_max[change_column][1])
                change_entry(str(change_id), column_names[change_column], str(new_int))
            elif column_types[change_column] == 'TEXT':
                new_text = input_text(prompt,column_justify[change_column]-1 )
                change_entry(str(change_id), column_names[change_column], new_text)
            find_in_db(({'ID':str(change_id)}, {}))
            print_cursor_data("Changed entry", c)
    elif choice == 4:
        #Delete a car from the database
        del_id = input_integer("Enter ID number of car to be deleted")
        find_in_db(({'ID':str(del_id)}, {}))    #Search database for ID number
        record_exists = c.fetchone()
        if record_exists is None:
            print("Invalid ID number {}".format(del_id))
        else:
            delete_car(del_id)
    elif choice == 5:
        #Search database
        #At this time searching is done by (a set of) data values on ..
        #.. *one* column only
        text_search = {}
        int_search = {}
        search_column = enter_column_number("Enter search column name", True)

        if column_types[search_column] == 'INTEGER':
            int_min_max = input_min_max_int(search_column)
            int_search[column_names[search_column]] = int_min_max
        elif column_types[search_column] == 'TEXT':
            new_text = input_text(column_names[search_column])
            text_search[column_names[search_column]] = new_text
        else:
            print("Unexpected type {}\n".format(column_types[search_column]))
            break
        find_in_db((text_search, int_search))
        print_cursor_data("Search Results", c)

#Finally, close the cursor & connection to the database
c.close()

conn.close()
