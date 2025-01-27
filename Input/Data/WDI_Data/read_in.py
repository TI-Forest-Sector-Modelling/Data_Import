import pandas as pd
import numpy as np
from  tqdm import tqdm
import os
import time
from itertools import product
import matplotlib.pyplot as plt
from enum import Enum
import datatable as dt
import pyarrow
import fastparquet

def start_process(new_path: bool = False, set_path_to: str = ""):
    """Generate starting time annd set directory
    """
    global start_time
    start_time = time.time()
    if new_path:
        path = set_path_to
    else:
        path = os.path.abspath(os.getcwd())
    os.chdir(path)

def read_data(folder: str, file: str):
    try:
        file_unformatted = str(file + "_unformatted")
        data = pd.read_parquet(str(folder + file_unformatted + ".parquet")) 
    except FileNotFoundError:
        try:
            data = pd.read_csv(str(folder + file + ".csv"))
            data = reformat_wdi_data(data)
            ResultWriter(data, folder, file_unformatted)
        except FileNotFoundError:
            print("No data found in directory! Please download data bulk from FAOSTat to this directoy: " + os.path.abspath(os.getcwd()))
    return data

def reformat_wdi_data(data: pd.DataFrame):
    data.iloc[:,0:4] = data.iloc[:,0:4].astype("category")
    data = data.rename(columns = {"Country Name": "Country_Name", "Country Code": "Country_Code", "Indicator Name": "Indicator_Name", "Indicator Code": "Indicator_Code"})
    data.iloc[:,4:] = data.iloc[:,4:].astype("float32")
    return data

def ResultWriter(data_all: pd.DataFrame, folder: str, file: str):
    data_all.to_parquet(str(folder + file + ".parquet"))

def end_process():
    end_time = time.time()
    print("This is the end!")
    print("--- %s seconds ---" % round((end_time - start_time),2))

def vectorize_dataset(data: pd.DataFrame):
    col_info = data.iloc[:,0:4].columns.to_list()
    col_values = data.iloc[:,4:].columns.to_list()
    temp_list_values = []
    temp_list_year = []
    temp_list_info = []
    for indicator in tqdm(data.Indicator_Code.unique()):
        data_indicator = data[data.Indicator_Code == indicator]
        for country in data_indicator.Country_Code.unique():
            data_country = data_indicator[data_indicator.Country_Code == country]
            data_country_info = data_country[col_info]
            data_country_values = data_country[col_values]
            data_country_transposed = data_country_values.transpose()
            data_values = data_country_transposed.values.tolist()
            data_year = data_country_values.columns.values.tolist()
            temp_list_values.extend(data_values)
            temp_list_year.extend(data_year)
            temp_list_info_help = []
            for info in data_country_info.values:
                help_info = [0] * len(col_values)
                for i in range(len(col_values)):
                    help_info[i] = info
                temp_list_info_help.extend(help_info)
            temp_list_info.extend(temp_list_info_help)
    data_reformatted = pd.concat([pd.DataFrame(temp_list_info),pd.DataFrame(temp_list_year),pd.DataFrame(temp_list_values)], axis = 1)
    print(data_reformatted)
    data_reformatted.info()
    data_reformatted.columns = ["Country_Name", "WDI_ISO3", "Indicator_Name", "Indicator_Code", "Year", "Value"]
    return data_reformatted

def downcasting(data: pd.DataFrame):
    data.Country_Name = data.Country_Name.astype("category")
    data.WDI_ISO3 = data.WDI_ISO3.astype("category")
    data.Indicator_Name = data.Indicator_Name.astype("category")
    data.Indicator_Code = data.Indicator_Code.astype("category")
    data.Value = data.Value.astype("float32")
    data = data.dropna()
    data.Year = data.Year.astype("int16")
    return data

def read_data_vector(data: pd.DataFrame, folder: str, file: str):
    try:
        data_vector = pd.read_parquet(str(folder + file + ".parquet")) 
    except FileNotFoundError:
        data_vector = vectorize_dataset(data)
        data_vector = downcasting(data_vector)
        ResultWriter(data_vector, folder, file)
    return data_vector

def main():
    folder = "WDI_Data\\"
    file = "WDIData"
    start_process()
    data = read_data(folder, file)
    data_vector = read_data_vector(data, folder, file)
    print(data_vector)
    data_vector.info()
    data_deu = data_vector[data_vector.WDI_ISO3 == "RUS"]
    data_deu_gdppc = data_deu[data_deu.Indicator_Code == "NY.GDP.PCAP.KD.ZG"] #"NY.GDP.PCAP.CD"
    print(data_deu_gdppc)
    plot_title = str(data_deu_gdppc.Indicator_Name.iloc[0] + " " + data_deu_gdppc.Country_Name.iloc[0])
    data_deu_gdppc.plot.line(x='Year', y='Value', title = plot_title)
    plt.show()
    end_process()

main()