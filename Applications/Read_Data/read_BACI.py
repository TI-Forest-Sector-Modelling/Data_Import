import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from pathlib import Path
from Applications.Read_Data.ProcessManager import ProcessManager
from Input.Dictionaries.hscodes import commodity_list

class BACIProcessor:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.pm = ProcessManager()

    def merge_data_and_info(self, country_info: pd.DataFrame, product_info: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        country_info = country_info[["country_code", "iso_3digit_alpha", "country_name_full"]]

        data_merged = data.merge(country_info, how="left", left_on="Reporter_Code", right_on="country_code")
        data_merged = data_merged.rename(columns={"iso_3digit_alpha": "Reporter_ISO3", "country_name_full": "Reporter_Name"})

        data_merged = data_merged.merge(country_info, how="left", left_on="Partner_Code", right_on="country_code")
        data_merged = data_merged.rename(columns={"iso_3digit_alpha": "Partner_ISO3", "country_name_full": "Partner_Name"})

        data_merged = data_merged.merge(product_info, how="left", left_on="HSCode", right_on="code")
        data_merged = data_merged.rename(columns={"description": "Product_Name"})

        data_merged["Product_Name"] = data_merged["Product_Name"].astype(str)

        return data_merged[["Year", "Reporter_Code", "Reporter_ISO3", "Reporter_Name", 
                            "Partner_Code", "Partner_ISO3", "Partner_Name", 
                            "HSCode", "HS_System", "Product_Name", "Value", "Quantity"]]

    def build_commodity_list(self) -> list:
        flat_commodity_list = [code for entry in commodity_list if isinstance(entry.get('hs02_codes', None), list) for code in entry['hs02_codes']]
        return list(set(flat_commodity_list))  # Remove duplicates

    def read_baci_data(self) -> pd.DataFrame:
        csv_files = [f for f in os.listdir(self.input_path) if f.endswith('.csv')]
        flat_commodity_list = self.build_commodity_list()
        dataframes = []

        for file in csv_files:
            input_file_path = os.path.join(self.input_path, file)
            print(f"Reading data file: {file}")

            df = self.pm.read_original_data(input_path=input_file_path)
            df = df[df["k"].isin(flat_commodity_list)]  # Filter by commodity list

            print(f"Data points in {file}: {len(df)}")
            dataframes.append(df)

        data = pd.concat(dataframes, ignore_index=True)
        data.columns = ["Year", "Reporter_Code", "Partner_Code", "HSCode", "Value", "Quantity"]
        return data

    def downcast_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data["Quantity"] = pd.to_numeric(data["Quantity"], errors="coerce")  # Convert string NA to NaN
        data.dropna(inplace=True)

        data = data.astype({
            "Year": "int16",
            "Reporter_Code": "int16",
            "Partner_Code": "int16",
            "HSCode": "int32",
            "Value": "float32",
            "Quantity": "float32"
        })
        return data

    def process_data(self, file_name: str = "BACI_DATA_as_vector") -> None:
        data = self.read_baci_data()
        data = self.downcast_data(data)
        self.pm.save_result(data=data, path=self.output_path, file_name=file_name)

if __name__ == "__main__":
    INPUT_PATH = r"E:\Data_Official_Reports\BACI"
    OUTPUT_PATH = Path(__file__).parent.parent.parent / "Output"

    processor = BACIProcessor(input_path=INPUT_PATH, output_path=OUTPUT_PATH)
    processor.process_data()