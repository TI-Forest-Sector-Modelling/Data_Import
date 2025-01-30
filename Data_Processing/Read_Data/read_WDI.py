import pandas as pd
import numpy as np
from tqdm import tqdm
from pathlib import Path
from Data_Processing.Read_Data.ProcessManager import ProcessManager
pm = ProcessManager()

class WDIDataProcessor:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path

    def reformat_wdi_data(self, data: pd.DataFrame) -> pd.DataFrame:
        for col in data.columns[:4]:
            data[col] = data[col].astype("category")
        data = data.rename(columns={"Country Name": "Country_Name",
                                    "Country Code": "Country_Code",
                                    "Indicator Name": "Indicator_Name",
                                    "Indicator Code": "Indicator_Code"})
        data.iloc[:, 4:] = data.iloc[:, 4:].apply(pd.to_numeric, downcast="float", errors="coerce")
        return data

    def vectorize_dataset(self, data: pd.DataFrame) -> pd.DataFrame:
        col_info = data.iloc[:, 0:4].columns.to_list()
        col_values = data.iloc[:, 4:].columns.to_list()
        temp_list_values = []
        temp_list_year = []
        temp_list_info = []

        for indicator in tqdm(data.Indicator_Code.unique(), desc="Processing Indicators"):
            data_indicator = data[data.Indicator_Code == indicator]
            for country in data_indicator.Country_Code.unique():
                data_country = data_indicator[data_indicator.Country_Code == country]
                data_country_info = data_country[col_info]
                data_country_values = data_country[col_values]
                data_country_transposed = data_country_values.transpose()
                data_values = data_country_transposed.values.tolist()
                data_year = data_country_values.columns.values.tolist()

                temp_list_values.extend(data_values)
                temp_list_year.extend(data_year)

                temp_list_info_help = []
                for info in data_country_info.values:
                    help_info = [info] * len(col_values)
                    temp_list_info_help.extend(help_info)

                temp_list_info.extend(temp_list_info_help)

        data_reformatted = pd.concat([
            pd.DataFrame(temp_list_info),
            pd.DataFrame(temp_list_year),
            pd.DataFrame(temp_list_values)
        ], axis=1)

        data_reformatted.columns = ["Country","WDI_ISO3", "Indicator","Indicator_Code", "Year", "Value"]
        data_reformatted = data_reformatted[["WDI_ISO3", "Indicator_Code", "Year", "Value"]]
        return data_reformatted

    def downcast_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data["WDI_ISO3"] = data["WDI_ISO3"].astype("category")
        data["Indicator_Code"] = data["Indicator_Code"].astype("category")
        data.loc[:, "Year"] = pd.to_numeric(data["Year"], downcast="integer", errors="coerce")
        data.loc[:, "Value"] = pd.to_numeric(data["Value"], downcast="float", errors="coerce")
        data = data.dropna()
        return data

    def main_process(self, file_name: str = "WDI_DATA_as_vector") -> None:
        data = pm.read_original_data(input_path=self.input_path)
        data = self.reformat_wdi_data(data)
        data = self.vectorize_dataset(data)
        data = self.downcast_data(data)
        pm.save_result(data, path=self.output_path, file_name=file_name)
    

if __name__ == "__main__":
    pm.start_process()
    INPUTPATH = r"E:\Data_Official_Reports\WDI\WDICSV.csv"
    OUTPUTPATH = Path(__file__).parent.parent.parent / "Output"
    wdiDP = WDIDataProcessor(input_path=INPUTPATH, output_path=str(OUTPUTPATH))
    wdiDP.main_process()