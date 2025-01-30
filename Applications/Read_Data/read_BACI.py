import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from pathlib import Path
from Applications.Read_Data.ProcessManager import ProcessManager
from Input.Dictionaries.hscodes import commodity_list

class BACIProcessor:
    def __init__(self, input_path: str, output_path: str, add_info_path:str):
        self.input_path = input_path
        self.output_path = output_path
        self.add_info_path = add_info_path
        self.pm = ProcessManager()

    def read_add_info(self, country_file_name:str="baci_country_codes"):
        country_file= self.add_info_path / f"{country_file_name}.csv"
        self.add_country_info = self.pm.read_original_data(input_path=country_file)
        self.add_country_info = self.add_country_info[["country_code","country_iso3"]]
        self.country_dict = dict(zip(self.add_country_info["country_code"], self.add_country_info["country_iso3"]))

    def iso_codes_to_data(self) -> pd.DataFrame:
        self.data['Reporter_Code'] = self.data['Reporter_Code'].map(self.country_dict).fillna(self.data['Reporter_Code'])
        self.data['Partner_Code'] = self.data['Partner_Code'].map(self.country_dict).fillna(self.data['Partner_Code'])

    def build_commodity_list(self) -> list:
        flat_commodity_list = [code for entry in commodity_list if isinstance(entry.get('hs02_codes', None), list) for code in entry['hs02_codes']]
        return list(set(flat_commodity_list)) 

    def read_baci_data(self) -> None:
        csv_files = [f for f in os.listdir(self.input_path) if f.endswith('.csv')]
        flat_commodity_list = self.build_commodity_list()
        dataframes = []

        for file in csv_files:
            input_file_path = os.path.join(self.input_path, file)
            print(f"Reading data file: {file}")

            df = self.pm.read_original_data(input_path=input_file_path)
            df = df[df["k"].isin(flat_commodity_list)]
            dataframes.append(df)

        self.data = pd.concat(dataframes, ignore_index=True)
        self.data.columns = ["Year", "Reporter_Code", "Partner_Code", "HSCode", "Value", "Quantity"]

    def downcast_data(self) -> None:
        self.data["Quantity"] = pd.to_numeric(self.data["Quantity"], errors="coerce")  # Convert string NA to NaN
        self.data.dropna(inplace=True)

        self.data = self.data.astype({
            "Year": "int16",
            "Reporter_Code": "int16",
            "Partner_Code": "int16",
            "HSCode": "int32",
            "Value": "float32",
            "Quantity": "float32"
        })

    def process_data(self, file_name: str = "BACI_DATA_as_vector") -> None:
        self.read_add_info()
        self.read_baci_data()
        self.downcast_data()
        self.iso_codes_to_data()
        self.pm.save_result(data=self.data, path=self.output_path, file_name=file_name)

if __name__ == "__main__":
    INPUT_PATH = r"E:\Data_Official_Reports\BACI"
    OUTPUT_PATH = Path(__file__).parent.parent.parent / "Output"
    ADD_INFO_PATH = Path(__file__).parent.parent.parent / "Input/additional_info"

    processor = BACIProcessor(input_path=INPUT_PATH, output_path=OUTPUT_PATH, add_info_path=ADD_INFO_PATH)
    processor.process_data()