import pandas as pd
import numpy as np
from  tqdm import tqdm
import os
import time
from itertools import product
import matplotlib.pyplot as plt
from enum import Enum
import pyarrow
import fastparquet
from pathlib import Path
import os

def package_directory():
    PACKAGEDIR = Path(__file__).parent.absolute()
    return PACKAGEDIR
PACKAGEDIR = package_directory()

def merge_data_and_info(country_info: pd.DataFrame, product_info: pd.DataFrame, data: pd.DataFrame):
    country_info = country_info[["country_code", "iso_3digit_alpha", "country_name_full"]]
    data_merged = data.merge(country_info, how = "left", left_on = data.Reporter_Code, right_on = country_info.country_code)
    data_merged = data_merged.rename(columns={"key_0": "key_reporter","iso_3digit_alpha": "Reporter_ISO3", "country_name_full": "Reporter_Name"})
    data_merged = data_merged.merge(country_info, how = "left", left_on = data_merged.Partner_Code, right_on = country_info.country_code)
    data_merged = data_merged.rename(columns={"key_0": "key_partner","iso_3digit_alpha": "Partner_ISO3", "country_name_full": "Partner_Name"})
    data_merged = data_merged.merge(product_info, how = "left", left_on = data_merged.HSCode, right_on = product_info.code)
    data_merged = data_merged.rename(columns={"description": "Product_Name"})
    data_merged["Product_Name"] = data_merged["Product_Name"]#.str[:15]
    data = data_merged[["Year", "Reporter_Code", "Reporter_ISO3", "Reporter_Name", "Partner_Code" , "Partner_ISO3", "Partner_Name", "HSCode", "HS_System", "Product_Name", "Value", "Quantity"]]
    return data

def read_original_data(previous_folder: str, folder: str, subfolder: str, version: str):
    data_original = pd.DataFrame()
    for i in tqdm(range(2002,2032)):
        file = str("\\" + folder + subfolder + "\\" + folder + subfolder + "_Y"  + str(i) + version)
        print(file)
        filename = str(PACKAGEDIR) + file
        print(filename)
        try:
            product_filename = str(previous_folder + folder + subfolder + "\\product_codes" + subfolder + version)
            country_filename = str(previous_folder + folder + subfolder + "\\country_codes" + version)
            product_info = pd.read_csv(product_filename, encoding = "latin-1")
            country_info = pd.read_csv(country_filename, encoding = "latin-1")
            print("try1")
            try:
                product_info["code"] = product_info["code"].str.extract(pat="(\d+)", expand=False)
                product_info["code"] = product_info["code"].astype(int)
                print("try2")
            except AttributeError:
                print("Attribute Error") 
            data_original1 = pd.read_csv(filename, encoding = "latin-1")
            data_original1.columns = ["Year", "Reporter_Code", "Partner_Code", "HSCode", "Value", "Quantity"]
            data_original1["HS_System"] = subfolder[1:5]
            data_original = merge_data_and_info(country_info = country_info, product_info = product_info, data = data_original1)
            result_name = str(previous_folder + folder + subfolder + "\\" + folder + subfolder + str(i) + "_all.parquet")
            data_original.to_parquet(result_name)
        except FileNotFoundError:
            print(str(" Data for year " + str(i) + ": Not found in folder " + folder + subfolder))

def read_parquet_files(previous_folder: str, folder: str, subfolder: str):
    data_parquet = pd.DataFrame()
    for i in tqdm(range(2002,2032)):
        try:
            result_name = str(previous_folder + folder + subfolder + "\\" + folder + subfolder + str(i) + "_all.parquet")
            data_wood = pd.read_parquet(result_name)
            data_wood = data_wood[data_wood.HSCode >= 400000]
            data_wood = data_wood[data_wood.HSCode <= 500000]
            data_parquet = pd.concat([data_parquet, data_wood], axis = 0).reset_index(drop=True)
        except FileNotFoundError:
            pass 
    print(data_parquet)
    downcasting(data_parquet)
    data_parquet.to_parquet(str(previous_folder + folder + subfolder + "\\" + folder + subfolder + "_woodproducts.parquet"))

    return data_parquet

def readin_process():
    previous_folder = "BACI_Data\\"
    folder = "BACI"
    version = "_V202401b.csv"
    subfolders = ["_HS02", "_HS07", "_HS12", "_HS17", "_HS22"]
    subfolders = ["_HS02"]
    for subfolder in subfolders:
        try:    
            data = pd.read_parquet(str(previous_folder + folder + subfolder + "\\" + folder + subfolder + "_woodproducts.parquet"))
            print(data)
        except FileNotFoundError:
            read_original_data(previous_folder, folder, subfolder, version)
            data = read_parquet_files(previous_folder, folder, subfolder)
            print(data)
            data.info()

    return data

def downcasting(data: pd.DataFrame):
    data.Quantity = data.Quantity.replace("           NA", np.nan)
    data.Year = data.Year.astype("int16")
    data.Reporter_Code  = data.Reporter_Code.astype("int16")
    data.Reporter_ISO3  = data.Reporter_ISO3.astype("category")
    data.Reporter_Name = data.Reporter_Name.astype("category")
    data.Partner_Code = data.Partner_Code.astype("int16")
    data.Partner_ISO3 = data.Partner_ISO3.astype("category")
    data.Partner_Name = data.Partner_Name.astype("category")
    data.HSCode = data.HSCode.astype("int32")
    data.HS_System = data.HS_System.astype("category")
    data.Product_Name = data.Product_Name.astype("category")
    data.Value = data.Value.astype("float32")
    data.Quantity = data.Quantity.astype("float32")

if __name__ == "__main__":
    data = readin_process()
    filename=(str(PACKAGEDIR)+'/BACI_HS02/BACI_HS02_Y2002_V202401b.csv')
    #filename = 'e:/GFPM/Datenbanken/read-fao-data-bulk/Data/BACI_Data/BACI_HS02/BACI_HS02_Y2003_V202401b.csv'
    data_original1 = pd.read_csv(':\GFPM\Datenbanken\read-fao-data-bulk\Data\BACI_Data\BACI_HS02\BACI_HS02_Y2009_V202401b.csv', encoding = "latin-1")
    print(data_original1)