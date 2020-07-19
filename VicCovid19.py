# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 00:46:45 2020

@author: Michael Fu
"""
import requests
import pandas as pd
from datetime import datetime as dt

  
def fetch_data_from_URL_query():
    url = 'https://services1.arcgis.com/vHnIGBHHqDR6y0CR/arcgis/rest/services/Victorian_LGA_Cases/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&outSR=173&f=json'
    r = requests.get(url)
    return r.json()
    
def create_excel_with_LGA_data():
    r_json = fetch_data_from_URL_query()
    data = r_json['features']

    # data of LGA in VIC    
    integrated_data = []

    # Columns in csv
    lga_name = []
    population = []
    area_SQRKM = []

    for dic in data:
        one_data = {}

        one_data['LGA_name'] = dic['attributes']['LGA_NAME19']
        lga_name.append(dic['attributes']['LGA_NAME19'])

        one_data['Population'] = dic['attributes']['Population']
        population.append(dic['attributes']['Population'])

        one_data['Area(SQRKM)'] = dic['attributes']['AREASQKM19']
        area_SQRKM.append(dic['attributes']['AREASQKM19'])

        integrated_data.append(one_data)

    df = pd.DataFrame({'LGA_name': lga_name, 'Population': population, 'Area(SQRKM)': area_SQRKM})
    df.to_excel('covid_data_VIC.xlsx', index=False)
    return
        
    
def append_daily_cases(date):
    """this method will append new accumulative data as a new column to excel"""
    """the variable - date will be append to the column, just for recognizing the current date"""

    r_json = self.fetch_data_from_URL_query()
    data = r_json['features']

    # Columns in excel
    last_updated = []
    cases = []

    for dic in data:
        time = str(dic['attributes']['LastUpdated'])
        if time.isnumeric():
            time = time[:10]
            time = int(time)
            time = dt.fromtimestamp(time).strftime('%Y-%m-%d %I:%M:%S %p')                    
            last_updated.append(time)
        else:
            last_updated.append('null')
        cases.append(dic['attributes']['Cases'])

    with open('covid_data_VIC.xlsx', 'rb') as f:
        df = pd.read_excel(f, index=False)

    df['Last Updated'+date] = last_updated
    df['Cases '+date] = cases

    df.to_excel('covid_data_VIC.xlsx', index=False)
    return
   
