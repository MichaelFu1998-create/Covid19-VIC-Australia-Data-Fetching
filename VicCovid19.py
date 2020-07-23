# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 00:46:45 2020

@author: Michael Fu
"""
import requests
import pandas as pd
from datetime import timedelta as td, datetime as dt


EXCEL_FILE_NAME = 'covid_data_VIC.xlsx'
COLUMN_INCREASE_RATE = 'Increase Rate Between '
COLUMN_CASES = 'Cases '
COLUMN_NEW_CASES = 'New Cases '
PERCENTAGE = True

# --- Append New Data --- #


def fetch_data_from_URL_query(url):
    r = requests.get(url)
    return r.json()
    
    
def create_excel_with_LGA_data(excel_file_name = EXCEL_FILE_NAME):
    """the variable - name of the excel file, default is 'covid_data_VIC.xlsx'"""
    
    url = 'https://services1.arcgis.com/vHnIGBHHqDR6y0CR/arcgis/rest/services/Victorian_LGA_Cases/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'    
    r_json = fetch_data_from_URL_query(url)
    data = r_json['features']
    
    # Columns in excel
    lga_name = []
    population = []
    area_SQRKM = []

    for dic in data:
        lga_name.append(dic['attributes']['LGA_NAME19'])
        population.append(dic['attributes']['Population'])
        area_SQRKM.append(dic['attributes']['AREASQKM19'])
        
    df = pd.DataFrame({'LGA_name': lga_name, 'Population': population, 'Area(SQRKM)': area_SQRKM})
    df.to_excel(excel_file_name, index=False)
    return


def append_daily_cases(excel_file_name = EXCEL_FILE_NAME):
    """append new accumulative data as a new column to excel"""
    """append new daily cases as a new column to excel"""
    """the variable - name of the file to be appended data, default is 'covid_data_VIC.xlsx'"""
    
    url = 'https://services1.arcgis.com/vHnIGBHHqDR6y0CR/arcgis/rest/services/Victorian_LGA_Cases/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'
    r_json = fetch_data_from_URL_query(url)
    data = r_json['features']

    # Columns in excel
    last_updated = []
    cases = []
    
    index = 0
    date = ''
    for dic in data:
        time = str(dic['attributes']['LastUpdated'])
        if time.isnumeric():
            time = time[:10]
            time = int(time)
            time = dt.fromtimestamp(time).strftime('%Y-%m-%d %I:%M:%S %p')                    
            last_updated.append(time)
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
    
    
    yesterday_date = (dt.strptime(date, '%m-%d') - td(days=1)).strftime('%m-%d')      
    df['New Cases ' + date] =  df['Cases ' + date] - df['Cases ' + yesterday_date]
    
    df.to_excel(excel_file_name, index=False)
    return

    
def append_past_cases(txt_file_name, excel_file_name = EXCEL_FILE_NAME):
    with open(txt_file_name) as f:
        content = f.read()
        content = eval(content)
        data = content['features']
        print(data)
    
    # Columns in excel
    last_updated = []
    cases = []
    
    index = 0
    date = ''
    for dic in data:
        time = str(dic['attributes']['LastUpdated'])
        if time.isnumeric():
            time = time[:10]
            time = int(time)
            time = dt.fromtimestamp(time).strftime('%Y-%m-%d %I:%M:%S %p')                    
            last_updated.append(time)
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


# --- Excel Calculator --- #
    

def difference_between_two_dates(columnname_date1, columnname_date2, excel_file_name = EXCEL_FILE_NAME): 
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    date1 = columnname_date1[-5:]
    date2 = columnname_date2[-5:]     
    column_name = 'New Cases Between ' + date1 + '&' + date2
    df[column_name] = df[columnname_date2] - df[columnname_date1]
    df.to_excel(excel_file_name, index=False)
    return
   

def increase_rate_between_two_dates(columnname_date1, columnname_date2, excel_file_name = EXCEL_FILE_NAME, percentage = PERCENTAGE):
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
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
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    column_name = 'new cases per 100,000 ' + columnname_new_cases[-5:]
    df[column_name] = round((df[columnname_population] / 100000) / df[columnname_new_cases], 2)
    
    df.to_excel(excel_file_name, index=False)
    return  


# --- Prediction --- #  
    

def avg_increase_rate(predicted_date, no_of_days = 3, columnname_increase_rate = COLUMN_INCREASE_RATE, excel_file_name = EXCEL_FILE_NAME, percentage = PERCENTAGE, output_percentage = True):
    """ predicted_date parameter format : mm-dd e.g. 8th Jan. -> '01-08' """    
    
    """ no_of_days is number of days used to calculate the average increase rate """
    """ e.g. if predicted_date = '07-18' and no_of_days = 2 """
    """ then the method would calculate the avg. rate of 07-17 and 07-16 """

    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    df_sum_rate = None
    date = dt.strptime(predicted_date, '%m-%d')   
    for i in range(1, no_of_days + 1):
        date = date - td(days=1)
        name = columnname_increase_rate + str(date - td(days=1)) + '&' + str(date)
        
        if percentage:
            df_sum_rate += int(df[name][:-1]) / 100
        else:
            df_sum_rate += df[name]

    if output_percentage:
        return '{0}{1}'.format(round(df_sum_rate / no_of_days, 2) * 100, '%')     
    else:
        return round(df_sum_rate / no_of_days, 2)


def predicted_rate_avg_increase_rate(predicted_date, excel_file_name = EXCEL_FILE_NAME, show_percentage = True):
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False) 
    
    column_name = 'Predicted Increase Rate For ' + predicted_date
    
    if show_percentage:
        df[column_name] = avg_increase_rate(predicted_date)       
    else:
        df[column_name] = avg_increase_rate(predicted_date, output_percentage = False)
    
    df.to_excel(excel_file_name, index=False)    
    return


def predicted_cases_avg_increase_rate(predicted_date, columnname_cases = COLUMN_CASES, excel_file_name = EXCEL_FILE_NAME):
    date = dt.strptime(predicted_date, '%m-%d')   
    
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    column_name = 'Predicted Cases For ' + predicted_date
    column_case = columnname_cases + str(date - td(days=1))

    df[column_name] = (avg_increase_rate(predicted_date, output_percentage = False) + 1) * df[column_case]
    df.to_excel(excel_file_name, index=False)        
    return


def predicted_new_cases_avg_increase_rate(predicted_date, columnname_cases = COLUMN_NEW_CASES, excel_file_name = EXCEL_FILE_NAME):
    date = dt.strptime(predicted_date, '%m-%d')   
    
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    column_name = 'Predicted New Cases For ' + predicted_date
    column_case = columnname_cases + str(date - td(days=1))
    
    df[column_name] = (avg_increase_rate(predicted_date, output_percentage = False) + 1) * df[column_case]
    df.to_excel(excel_file_name, index=False)    
    return
