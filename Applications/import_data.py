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
import Dictionaries.hscodes as dict_com
import warnings
import sys

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'

class user_input(Enum):
    folder = "Data\\"

class user_input_baci(Enum):
    folder = "BACI"
    hs_system  = "_HS02"
    file = "_woodproducts"

class user_input_fao(Enum):
    folder = "FAO_Data"
    file = "Forestry_E_All_Data_reformatted"

class user_input_fra(Enum):
    folder = "FRA_Data"
    file = "FRA_Data"

class user_input_wdi(Enum):
    folder = "WDI_Data"
    file = "WDIData"

class user_input_gravity(Enum):
    folder = "Gravity_Data"
    file = "Gravity_V202211"

class user_input_results(Enum):
    folder_results = "Data_combined"
    file = "Data_combined"

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

def read_data(file_name: str, folder: str = user_input.folder.value):
    try:
        data = pd.read_parquet(str(folder + file_name + ".parquet"))
    except (FileNotFoundError or ValueError) as error:
        print(["There is no file in folder: ", str(folder + file_name + ".parquet")])
        sys.exit(1)
    return data

def read_fao(folder: str = user_input_fao.folder.value,
             file: str = user_input_fao.file.value):
    data_fao = read_data(str(folder + "\\" + file))
    country_info = pd.read_csv(user_input.folder.value + folder+"\\Country_Master.csv", encoding= 'unicode_escape')
    country_info = country_info[["FAO Code","ISO-Code"]].rename(columns={"FAO Code":"FAO_Code","ISO-Code":"ISO_Code"}).dropna()
    country_info.FAO_Code = country_info.FAO_Code.astype("int32")
    country_info.ISO_Code = country_info.ISO_Code.astype("category")
    data_fao = data_fao.merge(country_info, how = "left", left_on="Area_Codes", right_on="FAO_Code")
    data_fao = data_fao[["Area_Codes", "ISO_Code", "Area", "Item_Codes", "Item", "Year", 
                        "Import_Value", "Export_Value", "Production", "Import_Quantity", 
                        "Export_Quantity"]].rename(columns={"Item_Codes": "Item_Code"})
    data_fao_new = pd.DataFrame()
    for indicator in ["Import_Value", "Export_Value", "Production", "Import_Quantity", "Export_Quantity"]:
        data_fao_h = pd.concat([data_fao.iloc[:,:6],data_fao[indicator]],axis=1).rename(columns={indicator: "Value"})
        data_fao_h["Source"] = "FAO"
        data_fao_h["Indicator_Code"] = indicator
        data_fao_new = pd.concat([data_fao_new,data_fao_h],axis=0).dropna().reset_index(drop=True)
    data_fao_new["Partner_ISO"] = np.nan
    data_fao = data_fao_new[["Year", "ISO_Code", "Partner_ISO", "Item_Code", "Source", "Indicator_Code", "Value"]]
    data_fao = downcasting(data_fao)
    return data_fao

def read_baci(folder: str = user_input_baci.folder.value,
              hs_system: str = user_input_baci.hs_system.value,
              file: str = user_input_baci.file.value):
    data_baci = read_data(str(folder + "_Data\\" + folder + 
                              hs_system + "\\" + folder + 
                              hs_system + file))
    data_baci_new = pd.DataFrame()
    for indicator in ['Value', 'Quantity']:
        data_baci_h = pd.concat([data_baci.iloc[:,:-2],data_baci[indicator]],axis=1).rename(columns={indicator: "Value"})
        data_baci_h["Source"] = "BACI02"
        data_baci_h["Indicator_Code"] = indicator
        data_baci_new = pd.concat([data_baci_new,data_baci_h],axis=0).dropna().reset_index(drop=True)
    data_baci = data_baci_new[["Year", "Reporter_ISO3", "Partner_ISO3", "HSCode", "Source", "Indicator_Code", "Value"]]
    data_baci_new = pd.DataFrame()
    for i in range(0,len(dict_com.commodity_list)):
        baci_subset = data_baci[data_baci.HSCode.isin(dict_com.commodity_list[i]["hs02_codes"])]
        baci_subset["Item_Code"] = dict_com.commodity_list[i]["fao_code"]
        baci_subset["Code"] = (baci_subset.Year.astype(str) + baci_subset.Reporter_ISO3.astype(str) + 
                               baci_subset.Partner_ISO3.astype(str) + baci_subset.Indicator_Code.astype(str) + 
                               baci_subset.Item_Code.astype(str))
        baci_subset = baci_subset[["Code","Value"]].reset_index(drop=True)
        baci_group_subset = baci_subset.groupby(["Code"])["Value"].sum().reset_index()
        data_baci_new = pd.concat([data_baci_new,baci_group_subset],axis=0).dropna().reset_index(drop=True)
    data_baci_new["Year"] = data_baci_new["Code"].str[:4].astype("int32")
    data_baci_new["ISO_Code"] = data_baci_new["Code"].str[4:7].astype("category")
    data_baci_new["Partner_ISO"] = data_baci_new["Code"].str[7:10].astype("category")
    data_baci_new["Indicator_Code"] = data_baci_new["Code"].str[10:-4].astype("category")
    data_baci_new["Source"] = "BACI02"
    data_baci_new["Source"] = data_baci_new["Source"].astype("category")
    data_baci_new["Item_Code"] = data_baci_new["Code"].str[-4:].astype("int32")
    data_baci = data_baci_new[["Year", "ISO_Code", "Partner_ISO", "Item_Code", "Source", "Indicator_Code", "Value"]]
    data_baci = downcasting(data_baci)
    return data_baci

def read_fra(folder = user_input_fra.folder.value,
             file = user_input_fra.file.value):
    data_fra = read_data(str(folder + "\\" + file)).rename(columns={"iso3": "ISO_Code", "year": "Year"})
    data_fra_new = pd.DataFrame()
    for indicator in data_fra.columns[4:]:
        data_fra_h = pd.concat([data_fra[data_fra.columns[:4]],data_fra[indicator]],axis=1).rename(columns={indicator: "Value"})
        data_fra_h["Partner_ISO"] = np.nan
        data_fra_h["Item_Code"] = np.nan
        data_fra_h["Source"] = "FRA"
        data_fra_h["Indicator_Code"] = indicator
        data_fra_new = pd.concat([data_fra_new,data_fra_h],axis=0).reset_index(drop=True)
        data_fra_new = data_fra_new.replace("yes", 1)
        data_fra_new = data_fra_new.replace("no", 0)
        data_fra_new = data_fra_new.replace('', np.nan)
    data_fra_new["Partner_ISO"] = np.nan
    data_fra = data_fra_new[["Year", "ISO_Code", "Partner_ISO", "Item_Code", "Source", "Indicator_Code", "Value"]]
    data_fra = downcasting(data_fra)
    return data_fra

def read_wdi(folder = user_input_wdi.folder.value,
             file = user_input_wdi.file.value):
    data_wdi = read_data(str(folder + "\\" + file)).rename(columns={"WDI_ISO3": "ISO_Code"})
    data_wdi["Source"] = "WDI"
    data_wdi["Item_Code"] = np.nan
    data_wdi["Partner_ISO"] = np.nan
    data_wdi = data_wdi[["Year", "ISO_Code", "Partner_ISO", "Item_Code", "Source", "Indicator_Code", "Value"]]
    data_wdi = replace_na(data_wdi)
    data_wdi = downcasting(data_wdi)
    return data_wdi

def read_gravity(folder = user_input_gravity.folder.value,
                 file = user_input_gravity.file.value):
    data_gavity = read_data(str(folder + "\\" + file))
    data_gavity = downcasting(data_gavity)
    return data_gavity

def downcasting(data: pd.DataFrame):
    data.Year = data.Year.astype("int32")
    data.ISO_Code = data.ISO_Code.astype("category")
    data.Partner_ISO = data.Partner_ISO.astype("string")
    data.Item_Code = data.Item_Code.astype("category")
    data.Source = data.Source.astype("category")
    data.Indicator_Code = data.Indicator_Code.astype("category")
    data.Value = data.Value.astype("float32")
    return data

def readin_process(folder: str = user_input.folder.value,
                   file: str = user_input_results.file.value,
                   folder_results: str = user_input_results.folder_results.value):
    read_ins = [read_baci(), read_fao(), read_fra(), read_wdi(), read_gravity()]
    data_all = pd.DataFrame()
    for i in tqdm(range(len(read_ins))):
        dataset = read_ins[i]
        data_all = pd.concat([data_all,dataset], axis = 0).reset_index(drop=True)
    data_all = downcasting(data_all)
    data_all.info()
    data_all.to_parquet(str(folder + folder_results + "\\" + file + ".parquet"))

    return data_all

def end_process():
    end_time = time.time()
    print("This is the end!")
    print("--- %s seconds ---" % round((end_time - start_time),2))

def replace_na(data: pd.DataFrame):
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.replace([np.nan], 0, inplace=True)
    return data

def main():
    start_process()
    # data = readin_process()
    # print(data)
    # print(data.Source.unique())
    # 
    data_fao=read_fao()
    data_fao = data_fao[data_fao.Year > 2010]
    data_fao.info()
    data_fao.to_csv(str('fao_formatted.csv'))
    end_process()
main()