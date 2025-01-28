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


# Example usage:
if __name__ == "__main__":
    manager = ProcessManager()

    # Example DataFrame
    df = pd.DataFrame({"A": [1, 2, np.nan], "B": [np.inf, 5, -np.inf]})

    # Process Workflow
    manager.start_process(new_path=False)
    df_cleaned = manager.replace_na(df)
    manager.save_result(df_cleaned, path="./output", file_name="cleaned_data")
    manager.end_process()