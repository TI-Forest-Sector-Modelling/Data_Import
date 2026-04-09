import pandas as pd
import os
import pyarrow
import fastparquet

def read_original_data():
    try:
        pass
        #data = dt.fread("FRA_Data\\FRA_Years_2023_01_27.csv").to_pandas()
    except FileNotFoundError:
        print("No data found in directory! Please download data bulk from FAOSTat to this directoy: " + os.path.abspath(os.getcwd()))
    return data

def ResultWriter(data_all: pd.DataFrame):
    data_all.to_parquet("FRA_Data\\FRA_Data.parquet")

data = read_original_data()
ResultWriter(data)
data_wood = pd.read_parquet("FRA_Data\\FRA_Data.parquet")
print(data_wood)