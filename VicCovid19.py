# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 00:46:45 2020

@author: Michael Fu
"""
import requests
import pandas as pd
from datetime import datetime as dt


def fetch_data_from_URL_query(url):
    r = requests.get(url)
    return r.json()
    
    
def create_excel_with_LGA_data(excel_file_name = 'covid_data_VIC.xlsx'):
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


def append_daily_cases(excel_file_name = 'covid_data_VIC.xlsx'):
    """append new accumulative data as a new column to excel"""
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

    df.to_excel(excel_file_name, index=False)
    return


def append_past_cases(txt_file_name, excel_file_name = 'covid_data_VIC.xlsx'):
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
