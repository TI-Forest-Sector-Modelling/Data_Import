import pandas as pd
from pathlib import Path
from Applications.import_data.import_data import DataProcessor

class DataImporter:
    def __init__(self, file_list:list, output_folder=None):
        self.file_list = file_list
        self.output_folder = output_folder or Path(__file__).parent.parent.parent / "Output"

    def import_data(self, file_name):
        file_path = self.output_folder / file_name
        print(f"Checking file: {file_path}")

        if file_path.exists():
            print(f"{file_name} exists in {self.output_folder}; Data will be imported.")
        else:
            print(f"{file_name} does NOT exist in {self.output_folder}; Processing from CSV files.")
            processor = DataProcessor(output_path=self.output_folder)
            processor.run()
        
        return pd.read_parquet(file_path)

    def main_process(self):
        results = {f"{file_name[:3].upper()}_data": self.import_data(file_name) for file_name in self.file_list}
        return results

if __name__ == "__main__":
    file_list = ["BACI_DATA_as_vector.parquet","FAO_DATA_as_vector.parquet","WDI_DATA_as_vector.parquet"]
    
    importer = DataImporter(file_list=file_list)
    results = importer.main_process()
    print(results)

