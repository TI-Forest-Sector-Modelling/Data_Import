import pandas as pd
import numpy as np
import os
import time
from pathlib import Path

class ProcessManager:
    def __init__(self,commodity_list:list=[]):
        self.start_time = None
        self.commodity_list = commodity_list

    def start_process(self, new_path: bool = False, set_path_to: str = ""):
        self.start_time = time.time()
        if new_path:
            if not os.path.exists(set_path_to):
                raise FileNotFoundError(f"Specified path does not exist: {set_path_to}")
            path = set_path_to
        else:
            path = os.path.abspath(os.getcwd())
        os.chdir(path)
        print(f"Process started...")

    def read_original_data(self, input_path):
        try:
            data = pd.read_csv(input_path, encoding="latin-1")
            print("Data read successfully!")
        except FileNotFoundError:
            print(f"No data found in directory! Please ensure the file exists at: {input_path}")
            raise
        return data

    def replace_na(self, data: pd.DataFrame) -> pd.DataFrame:
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna(0, inplace=True)
        return data
    
    def remove_duplicates_from_dict(self, data_dict: dict):
        """Entfernt Duplikate aus einem Dictionary."""
        unique_dict = {}
        seen_values = set()
        for key, value in data_dict.items():
            if value not in seen_values:
                unique_dict[key] = value
                seen_values.add(value)
        return unique_dict

    def replace_column_data_with_dict(self, data: pd.DataFrame, mapping_dict: dict, column_name: str = 'Area_Code'):
        """Ersetzt Werte in einer DataFrame-Spalte basierend auf einem Mapping-Dictionary."""
        data[column_name] = data[column_name].map(mapping_dict).fillna(data[column_name])
        return data

    def hs_to_fao_dict(self):
        """Erstellt eine Zuordnung von HS-Codes zu FAO-Codes."""
        hs_to_fao_map = {}
        for entry in self.commodity_list:
            for hs_code in entry["hs02_codes"]:
                hs_to_fao_map[hs_code] = entry["fao_code"]
        return dict(sorted(hs_to_fao_map.items()))

    def read_additional_info(self, add_input_path: Path, country_file_name: str = "Country_Master"):
        """Liest zusätzliche Länderinformationen ein und erstellt ein Mapping."""
        country_file = add_input_path / f"{country_file_name}.csv"
        add_country_info = self.read_original_data(input_path=country_file)
        add_country_info = add_country_info[["FAO Code", "ISO-Code"]]
        country_info_dict = dict(zip(add_country_info["FAO Code"], add_country_info["ISO-Code"]))
        return self.remove_duplicates_from_dict(country_info_dict)

    def save_result(self, data: pd.DataFrame, path: str, file_name: str):
        output_path = Path(path)
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        csv_path = output_path / f"{file_name}.csv"
        parquet_path = output_path / f"{file_name}.parquet"
        
        data.to_csv(csv_path, index=False)
        data.to_parquet(parquet_path, index=False)
        
        print(f"Results saved to: \n - {csv_path}\n - {parquet_path}")

    def end_process(self):
        if self.start_time is None:
            raise ValueError("The process has not been started. Use `start_process` first.")
        
        end_time = time.time()
        elapsed_time = round(end_time - self.start_time, 2)
        print("Process completed!")
        print(f"--- {elapsed_time} seconds ---")