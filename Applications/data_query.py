import pandas as pd
from pathlib import Path
from Applications.import_data.data_distribution import DataImporter

def data_import(file_list:list):
    importer = DataImporter(file_list=file_list)
    results = importer.main_process()
    return results

file_list = ["BACI_DATA_as_vector.parquet",
             "FAO_DATA_as_vector.parquet",
             "WDI_DATA_as_vector.parquet"]

data_dict = data_import(file_list=file_list)
print(data_dict)

