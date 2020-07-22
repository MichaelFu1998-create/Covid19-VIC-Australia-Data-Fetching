# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 15:23:27 2020

@author: michael
"""
import pandas as pd


def difference_between_two_dates(columnname_date1, columnname_date2, excel_file_name = 'covid_data_VIC.xlsx'): 
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    date1 = columnname_date1[-5:]
    date2 = columnname_date2[-5:]     
    column_name = 'New Cases Between ' + date1 + '&' + date2
    df[column_name] = df[columnname_date2] - df[columnname_date1]
    df.to_excel(excel_file_name, index=False)
    return
   

def increase_rate_between_two_dates(columnname_date1, columnname_date2, excel_file_name = 'covid_data_VIC.xlsx', percentage = True):
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


def new_cases_per_100000people(columnname_new_cases, columnname_population= 'Population', excel_file_name = 'covid_data_VIC.xlsx'):
    with open(excel_file_name, 'rb') as f:
        df = pd.read_excel(f, index=False)
    
    column_name = 'new cases per 100,000 ' + columnname_new_cases[-5:]
    df[column_name] = round((df[columnname_population] / 100000) / df[columnname_new_cases], 2)
    
    df.to_excel(excel_file_name, index=False)
    return