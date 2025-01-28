import pandas as pd
import numpy as np
import os
import time
from pathlib import Path


class ProcessManager:
    def __init__(self):
        self.start_time = None

    def start_process(self, new_path: bool = False, set_path_to: str = ""):
        self.start_time = time.time()
        if new_path:
            if not os.path.exists(set_path_to):
                raise FileNotFoundError(f"Specified path does not exist: {set_path_to}")
            path = set_path_to
        else:
            path = os.path.abspath(os.getcwd())
        os.chdir(path)
        print(f"Process started at {path}")

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