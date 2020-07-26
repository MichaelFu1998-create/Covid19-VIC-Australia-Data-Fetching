import VicCovid19
import pandas as pd
from datetime import timedelta as td, datetime as dt
import matplotlib.pyplot as plt


# --- default value for methods --- #


EXCEL_FILE_NAME = VicCovid19.EXCEL_FILE_NAME
COLUMN_CASES = VicCovid19.COLUMN_CASES
COLUMN_LGA = 'LGA_name'

# --- plotting methods --- #


def daily_new_cases(start_date, end_date, lga_name, columnname_lga = COLUMN_LGA, columnname_cases = COLUMN_CASES, excel_file_name = EXCEL_FILE_NAME):
    """
    retrieve data from an excel and generate to two lists as axis X and Y

    Parameters
    ----------
    * special format is needed for start_date and end_date
    * special format : mm-dd e.g. 18th Jul -> 07-18
    * data are both inclusive for start date and end date
    start_date : str
        the first date to be plotted
    end_date : str
        the last date to be plotted

    columnname_lga : str
        name of column which contains the local government name
    columnname_cases : str
        name of column which contains the data of accumulative cases
    excel_file_name : str
        file name of the excel to be processed

    Returns
    ----------
    return 2D-list containing the data of axis X and Y
    """

    start_date = dt.strptime(start_date, '%m-%d')                    
    end_date = dt.strptime(end_date, '%m-%d')
    
    # data to be drawn in the line graph
    x_date = []
    y_cases = []

    with open(EXCEL_FILE_NAME, 'rb') as f:
        df = pd.read_excel(f, index=False)

    # keep updating current_date in for-loop to find the right column in excel
    # change data type to str and parse index 5-9 to get the format of 'mm-dd'
    current_date = str(start_date)[5:10]
    no_of_days = end_date - start_date
    for i in range (no_of_days.days + 1):
        column_name = columnname_cases + current_date

        x_date.append(current_date)
        y_cases.append(int(df[column_name].loc[df[columnname_lga] == lga_name].to_list()[0]))

        current_date = dt.strptime(current_date, '%m-%d') + td(days=1)       
        current_date = str(current_date)[5:10]

    data = []
    data.append(x_date)
    data.append(y_cases)
    return data


def one_line_graph(start_date, end_date, lga_name, columnname_lga = COLUMN_LGA, columnname_cases = COLUMN_CASES, excel_file_name = EXCEL_FILE_NAME):
    data = daily_new_cases(start_date, end_date, lga_name, columnname_lga = COLUMN_LGA, columnname_cases = COLUMN_CASES)
    x_date = data[0]
    y_cases = data[1]

    plt.plot(x_date, y_cases)
    plt.show()

def two_line_graph(start_date, end_date, lga_name1, lga_name2, columnname_lga = COLUMN_LGA, columnname_cases = COLUMN_CASES, excel_file_name = EXCEL_FILE_NAME):
    data = daily_new_cases(start_date, end_date, lga_name1, columnname_lga = COLUMN_LGA, columnname_cases = COLUMN_CASES)
    x1_date = data[0]
    y1_cases = data[1]
    
    data = daily_new_cases(start_date, end_date, lga_name2, columnname_lga = COLUMN_LGA, columnname_cases = COLUMN_CASES)
    x2_date = data[0]
    y2_cases = data[1]    
    
    plt.plot(x1_date, y1_cases, x2_date, y2_cases)
    plt.show()   


two_line_graph('07-19', '07-21', 'Brimbank (C)', 'Hume (C)')
