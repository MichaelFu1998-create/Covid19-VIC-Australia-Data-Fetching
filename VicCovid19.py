# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 00:46:45 2020

@author: Michael Fu
"""
import requests
import pandas as pd
from datetime import timedelta as td, datetime as dt


# --- default value for methods --- #


EXCEL_FILE_NAME = 'covid_data_VIC.xlsx'
COLUMN_INCREASE_RATE = 'Increase Rate Between '
COLUMN_CASES = 'Cases '
COLUMN_NEW_CASES = 'New Cases '
PERCENTAGE = True
NO_OF_DAYS_FOR_AVG_RATE = 3


# --- Append New Data --- #


def fetch_data_from_URL_query(url):
    """
    fetch data from specific address

    Parameters
    ----------
    url : str
        the URL query address
        
    Returns
    -------
    json-formatted data from the URL
    """
    
    r = requests.get(url)
    return r.json()
    
    
def create_excel_with_LGA_data(excel_file_name = EXCEL_FILE_NAME):
    """
    take in a parameter as the file name for the excel created by this method
    this method generate COVID19 data in VIC, AU from URL query
    process the json-format data to tabular data
    use pandas dataframe to output the tabular data to an excel file

    Parameters
    ----------
    excel_file_name : str
        file name of the excel
    """
    
    url = 'https://services1.arcgis.com/vHnIGBHHqDR6y0CR/arcgis/rest/services/Victorian_LGA_Cases/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'    
    r_json = fetch_data_from_URL_query(url)
    data = r_json['features']
    
    # store data into list, to make data tabular
    lga_name = []
    population = []
    area_SQRKM = []

    for dic in data:
        lga_name.append(dic['attributes']['LGA_NAME19'])
        population.append(dic['attributes']['Population'])
        area_SQRKM.append(dic['attributes']['AREASQKM19'])
    
    # specify columns in the excel    
    df = pd.DataFrame({'LGA_name': lga_name, 'Population': population, 'Area(SQRKM)': area_SQRKM})
    df.to_excel(excel_file_name, index=False)
    return


def append_daily_cases(excel_file_name = EXCEL_FILE_NAME):
    """
    fetch new data from query URL
    make json-format data tabular 
    append new accumulative data as a new column to excel
    append new daily cases as a new column to excel

    Parameters
    ----------
    excel_file_name : str
        file name of the excel which would be appended new data
    """
    
    url = 'https://services1.arcgis.com/vHnIGBHHqDR6y0CR/arcgis/rest/services/Victorian_LGA_Cases/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'
    r_json = fetch_data_from_URL_query(url)
    data = r_json['features']

    # store data into list, to make data tabular
    last_updated = []
    cases = []
    
    index = 0
    date = ''
    for dic in data:
        time = str(dic['attributes']['LastUpdated'])
        # in case there are some non-numeric values e.g. null 
        if time.isnumeric():
            # change json-like time to datetime-like time
            time = time[:10]
            time = int(time)
            time = dt.fromtimestamp(time).strftime('%Y-%m-%d %I:%M:%S %p')                    
            last_updated.append(time)
            # retrieve time value once as the new column name in excel
            if index == 0:
                date = time[5:10]
                index = 1
        else:
            last_updated.append('null')
        cases.append(dic['attributes']['Cases'])

    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)

    df['Last Updated ' + date] = last_updated
    df['Cases ' + date] = cases
    
    # to get the new cases today
    # have to substract cases yesterday
    yesterday_date = (dt.strptime(date, '%m-%d') - td(days=1)).strftime('%m-%d')      
    df['New Cases ' + date] =  df['Cases ' + date] - df['Cases ' + yesterday_date]
    
    df.to_excel(excel_file_name, index=False)
    return

    
def append_past_cases(txt_file_name, excel_file_name = EXCEL_FILE_NAME):
    """
    fetch new data from existing txt file in the folder 'covid_data_json'
    make json-format data tabular 
    append the date of the case as a new column to excel
    append new accumulative data as a new column to excel

    Parameters
    ----------
    txt_file_name : str
        the name of txt file that contains the data to be read
    excel_file_name : str
        file name of the excel which would be appended new data
    """
    
    with open(txt_file_name) as f:
        content = f.read()
        content = eval(content)
        data = content['features']
        print(data)
    
    # store data into list, to make data tabular
    last_updated = []
    cases = []
    
    index = 0
    date = ''
    for dic in data:
        time = str(dic['attributes']['LastUpdated'])
        # in case there are some non-numeric values e.g. null 
        if time.isnumeric():
            # change json-like time to datetime-like time
            time = time[:10]
            time = int(time)
            time = dt.fromtimestamp(time).strftime('%Y-%m-%d %I:%M:%S %p')                    
            last_updated.append(time)
            # retrieve time value once as the new column name in excel           
            if index == 0:
                date = time[5:10]
                index = 1
        else:
            last_updated.append('null')
        cases.append(dic['attributes']['Cases'])

    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)

    df['Last Updated ' + date] = last_updated
    df['Cases ' + date] = cases

    df.to_excel(excel_file_name, index=False)
    return


# --- Excel Calculation --- #
    

def difference_between_two_dates(columnname_date1, columnname_date2, excel_file_name = EXCEL_FILE_NAME): 
    """
    calculate the difference between two columns in the excel

    Parameters
    ----------
    columnname_date1 : str
        column containing numbers of minus from
    columnname_date2 : str
        column containing numbers of minus
    excel_file_name : str
        file name of the excel which would be appended new data (difference between the two)
    """    
    
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    # retrieve the date value(last 5 chars) from column name
    date1 = columnname_date1[-5:]
    date2 = columnname_date2[-5:]     
    column_name = 'New Cases Between ' + date1 + '&' + date2
    df[column_name] = df[columnname_date2] - df[columnname_date1]
    df.to_excel(excel_file_name, index=False)
    return
   
    
def increase_rate_between_two_dates(columnname_date1, columnname_date2, excel_file_name = EXCEL_FILE_NAME, percentage = PERCENTAGE):
    """
    calculate the difference between two columns in the excel

    Parameters
    ----------
    columnname_date1 : str
        column containing original data (data before)
    columnname_date2 : str
        column containing increased data (data after)
    excel_file_name : str
        file name of the excel which would be appended new data (increase rate)
    percentage : bool
        True -- show the percentage -- e.g.1%
        False -- show the numeric value -- e.g.0.01
    """     
  
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)

    # retrieve the date value(last 5 chars) from column name
    date1 = columnname_date1[-5:]
    date2 = columnname_date2[-5:]
    column_name = 'Increase Rate Between ' + date1 + '&' + date2
    
    if percentage:
        df[column_name] = '{0}{1}'.format(round((df[columnname_date2] - df[columnname_date1]) / df[columnname_date1], 2) * 100, '%')        
    else:
        df[column_name] = round((df[columnname_date2] - df[columnname_date1]) / df[columnname_date1], 2)
    
    df.to_excel(excel_file_name, index=False)
    return


def new_cases_per_100000people(columnname_new_cases, columnname_population= 'Population', excel_file_name = EXCEL_FILE_NAME):
    """
    calculate the how many cases per 100,000 people are there in a single city

    Parameters
    ----------
    columnname_new_cases : str
        column containing data of new cases on specific date
    columnname_population : str
        column containing data of population in specific city
    excel_file_name : str
        file name of the excel which would be appended new data (new cases per 100,000 people)
    """ 
    
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    # [-5:] contains the date value
    column_name = 'new cases per 100,000 ' + columnname_new_cases[-5:]
    df[column_name] = round((df[columnname_population] / 100000) / df[columnname_new_cases], 2)
    
    df.to_excel(excel_file_name, index=False)
    return  


# --- Prediction --- #  
    

def avg_increase_rate(predicted_date, no_of_days = NO_OF_DAYS_FOR_AVG_RATE, columnname_increase_rate = COLUMN_INCREASE_RATE, excel_file_name = EXCEL_FILE_NAME, percentage = PERCENTAGE, output_percentage = True):
    """
    calculate the n days avg. increase rate before predicted date
    
    *there is a special format for predicted_date -> 'mm-dd'    
    e.g. if predicted_date = '07-18' and no_of_days = 2 
    then the method would calculate the avg. rate of 07-17 and 07-16 
    
    Parameters
    ----------
    predicted_date : str
        the date to be predicted
        format : mm-dd e.g. 8th Jan. -> '01-08'
    no_of_days : int
        no of days that would be used to calculate the avg increase rate
    columnname_increase_rate : str
        the partial name of the column which contains the value of increase rate
    excel_file_name : str
        name of file containing the data
    percentage : bool
        True -- the value(increase rate) to be calculated includes '%' symbol
        False -- the value(increase rate) to be calculated is all numeric
    output_percentage : bool
        True -- return the percentage -- e.g.1%
        False -- return the numeric value -- e.g.0.01
    
    Returns
    -------
    output_percentage is True >> return the percentage -- e.g.1%
    output_percentage is False >> return the numeric value -- e.g.0.01
    """ 
    
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    # summary of all of the increase rate  
    df_sum_rate = None
    date = dt.strptime(predicted_date, '%m-%d')   
    for i in range(1, no_of_days + 1):
        # use date of predicted date to find the date of last few days' 
        date = date - td(days=1)
        name = columnname_increase_rate + str(date - td(days=1)) + '&' + str(date)
        
        if percentage:
            # abandon the '%' symbol, only retrieve the number
            df_sum_rate += int(df[name][:-1]) / 100
        else:
            df_sum_rate += df[name]

    if output_percentage:
        return '{0}{1}'.format(round(df_sum_rate / no_of_days, 2) * 100, '%')     
    else:
        return round(df_sum_rate / no_of_days, 2)


def predicted_rate_avg_increase_rate(predicted_date, no_of_days = NO_OF_DAYS_FOR_AVG_RATE, excel_file_name = EXCEL_FILE_NAME, show_percentage = True):
    """
    the predicted rate calculated from avg. increase rate 
    output n-days avg. increase to an excel as a  new column
    
    *there is a special format for predicted_date -> 'mm-dd'
    e.g. if predicted_date = '07-18' and no_of_days = 2 
    then the method would calculate the avg. rate of 07-17 and 07-16 
    
    Parameters
    ----------
    predicted_date : str
        the date to be predicted
        format : mm-dd e.g. 8th Jan. -> '01-08'
    no_of_days : int
        no of days that would be used to calculate the avg increase rate
    excel_file_name : str
        name of the excel file to be processed
    show_percentage : bool
        True -- the rate contains '%' symbol
        False -- the rate is plain numeric value
    """
    
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False) 
    
    column_name = 'Predicted Increase Rate For ' + predicted_date
    
    if show_percentage:
        df[column_name] = avg_increase_rate(predicted_date, no_of_days)       
    else:
        df[column_name] = avg_increase_rate(predicted_date, no_of_days, output_percentage = False)
    
    df.to_excel(excel_file_name, index=False)    
    return


def predicted_cases_avg_increase_rate(predicted_date, no_of_days = NO_OF_DAYS_FOR_AVG_RATE, columnname_cases = COLUMN_CASES, excel_file_name = EXCEL_FILE_NAME):
    """
    the predicted accumulative cases calculated from avg. increase rate 
    calculate the n days avg. increase rate before predicted date
    use avg. rate to predict the accumulative cases for predicted_date
    and output to an excel as a new column
    
    *there is a special format for predicted_date -> 'mm-dd'
    e.g. if predicted_date = '07-18' and no_of_days = 2 
    then the method would calculate the avg. rate of 07-17 and 07-16 
    
    Parameters
    ----------
    predicted_date : str
        the date to be predicted
        format : mm-dd e.g. 8th Jan. -> '01-08'
    no_of_days : int
        no of days that would be used to calculate the avg increase rate
    columnname_cases : str
        the partial column name which contains the value of accumulative cases
    excel_file_name : str
        name of the excel file to be processed
    """
    
    date = dt.strptime(predicted_date, '%m-%d')   
    
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    # find the name of column containing the data on the date before predicted_date 
    column_name = 'Predicted Cases For ' + predicted_date
    column_case = columnname_cases + str(date - td(days=1))

    df[column_name] = (avg_increase_rate(predicted_date, no_of_days, output_percentage = False) + 1) * df[column_case]
    df.to_excel(excel_file_name, index=False)        
    return


def predicted_new_cases_avg_increase_rate(predicted_date, no_of_days = NO_OF_DAYS_FOR_AVG_RATE, columnname_cases = COLUMN_NEW_CASES, excel_file_name = EXCEL_FILE_NAME):
    """
    the predicted new cases calculated from avg. increase rate 
    calculate the n days avg. increase rate before predicted date
    use avg. rate to predict the new cases for predicted_date
    and output to an excel as a new column
    
    *there is a special format for predicted_date -> 'mm-dd'
    e.g. if predicted_date = '07-18' and no_of_days = 2 
    then the method would calculate the avg. rate of 07-17 and 07-16 
    
    Parameters
    ----------
    predicted_date : str
        the date to be predicted
        format : mm-dd e.g. 8th Jan. -> '01-08'
    no_of_days : int
        no of days that would be used to calculate the avg increase rate
    columnname_cases : str
        the partial column name which contains the value of new cases    
    excel_file_name : str
        name of the excel file to be processed
    """    
    
    date = dt.strptime(predicted_date, '%m-%d')   
    
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    # find the name of column containing the data on the date before predicted_date     
    column_name = 'Predicted New Cases For ' + predicted_date
    column_case = columnname_cases + str(date - td(days=1))
    
    df[column_name] = (avg_increase_rate(predicted_date, no_of_days, output_percentage = False) + 1) * df[column_case]
    df.to_excel(excel_file_name, index=False)    
    return