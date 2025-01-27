import pandas as pd
import numpy as np
from  tqdm import tqdm
import os
import time
from itertools import product
import matplotlib.pyplot as plt
import math
from enum import Enum
import datatable as dt
import pyarrow
import fastparquet

class user_input(Enum):
    folder = "Gravity_Data"

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

def read_data(folder_name: str, file_name: str):
    try:
        data = pd.read_csv(str(folder_name + '\\' + file_name + ".csv"))        
    except (FileNotFoundError or ValueError) as error:
        data = pd.DataFrame(["There is no such File in folder"])
    print(data)
    return data

def downcasting(data: pd.DataFrame):
    data.Year = data.Year.astype("int32")
    data.ISO_Code = data.ISO_Code.astype("category")
    data.Partner_ISO = data.Partner_ISO.astype("category")
    #data.Item_Code = data.Item_Code.astype("int32")
    data.Source = data.Source.astype("category")
    data.Indicator_Code = data.Indicator_Code.astype("category")
    data.Value = data.Value.astype("float32")
    return data

def ResultWriter(data_all: pd.DataFrame, folder: str, file: str):
    data_all.to_parquet(folder + '\\' + file + '.parquet')

def end_process():
    end_time = time.time()
    print("This is the end!")
    print("--- %s seconds ---" % round((end_time - start_time),2))

def main():
    start_process()

    folder = user_input.folder.value
    file = "Gravity_V202211"
    data = read_data(folder_name = folder, file_name=file)
    data = data[data.year >= 2002].reset_index(drop=True)
    describe = ['year', 'iso3_o', 'iso3_d']
    selection = ['distw_harmonic','distw_arithmetic', 'distw_harmonic_jh', 'distw_arithmetic_jh', 'dist', 'distcap', 
                 'contig','diplo_disagreement','scaled_sci_2021','comlang_off','comlang_ethno','comrelig','sibling_ever',
                 'gatt_o', 'gatt_d', 'wto_o', 'wto_d','eu_o', 'eu_d', 'fta_wto', 'fta_wto_raw','tradeflow_baci']
    data_gravity = pd.DataFrame()
    for col in tqdm(selection):
        data_cols = describe.copy()
        data_cols.append(col)
        data_h = data[data_cols].rename(columns={'year': 'Year','iso3_o': 'ISO_Code', 'iso3_d': 'Partner_ISO',col: 'Value'})
        data_h['Item_Code'] = np.nan
        data_h["Source"] = 'Gravity/CEPII'
        data_h['Indicator_Code'] = col
        data_h = data_h[["Year", "ISO_Code", "Partner_ISO", "Item_Code", "Source", "Indicator_Code", "Value"]]
        data_gravity = pd.concat([data_gravity, data_h],axis=0).reset_index(drop=True)
    data_gravity = downcasting(data=data_gravity)
    ResultWriter(data_all=data_gravity, folder=folder, file=file)
    print(data_gravity)
    data_gravity.info()

    end_process()

main()
