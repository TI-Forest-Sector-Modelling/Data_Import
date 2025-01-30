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

fao_data = data_dict["FAO_data"]
print(fao_data.Element_Code.unique())
# def read_add_info(self, country_file_name:str="Country_Master"):
#     country_file= self.add_input_path / f"{country_file_name}.csv"
#     self.add_country_info = pm.read_original_data(input_path=country_file)
#     self.add_country_info = self.add_country_info[["FAO Code","ISO-Code"]]
#     self.country_dict = dict(zip(self.add_country_info["FAO Code"], self.add_country_info["ISO-Code"]))

# def iso_codes_to_data(self) -> pd.DataFrame:
#     print(self.data)
#     self.data['Area_Code'] = self.data['Area_Code'].map(self.country_dict).fillna(self.data['Area_Code'])

