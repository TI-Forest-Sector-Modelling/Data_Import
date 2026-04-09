import os
from FSMDataImport.core.processes.ProcessManager import ProcessManager
pm = ProcessManager()
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from FSMDataImport.Input.path_names.paths import (
    url_faostat_update,
    fao_download_path,
    output_path,
    )

class FAODataProcessor:
    def __init__(self):
        self.input_path = fao_download_path
        self.output_path = output_path
        self.data = None

    def check_fao_updates(self):      
        response = requests.get(url_faostat_update)
        root = ET.fromstring(response.content)

        for dataset in root.findall(".//Dataset"):
            if dataset.find("DatasetCode").text =="FO":
                latest_update = datetime.fromisoformat(dataset.find("DateUpdate").text)
                latest_update = latest_update.strftime("%Y-%m-%d")
        return latest_update

    def reformat_data(self):
        if self.data is None:
            raise ValueError("No data to reformat. Please run `read_original_data` first.")

        print("\nStart reformatting original data to long format")
        data = self.data.dropna(how="all", axis=1)

        value_cols = data.filter(regex="^Y").columns
        id_vars = [col for col in data.columns if col not in value_cols]

        data_long = data.melt(
            id_vars=id_vars,
            value_vars=value_cols,
            var_name="Year",
            value_name="Value"
        )

        data_long = data_long.rename(columns={
            "Area Code": "Area_Code",
            "Item Code": "Item_Code",
            "Element Code": "Element_Code"
        })

        data_long["Flag"] = data_long["Year"].str[-1:]
        data_long["Year"] = data_long["Year"].str.replace(r"\D", "", regex=True)

        data_long = data_long[~data_long["Flag"].isin(["F", "N"])]

        print("Reformatting done")

        self.data = data_long

    def save_reformatted_data(self, file_name: str = "FAO_DATA_as_vector"):
        """Save the reformatted data to the output path."""
        if self.data is None:
            raise ValueError("No data to save. Please process the data first.")
        
        pivoted_df = self.data[["Area","Area_Code","Item","Item_Code", "Element_Code", "Year", "Value"]]
        self.data = self.data[["Area_Code","Item_Code", "Element_Code", "Year", "Value"]]
        
        self.data["Area_Code"] = self.data["Area_Code"].astype("int64", copy=False)
        self.data["Item_Code"] = self.data["Item_Code"].astype("int64", copy=False)
        self.data["Year"] = self.data["Year"].astype("int64", copy=False)

        output_file = self.output_path / f"{file_name}.csv"
        pm.save_result(self.data, path=str(self.output_path), file_name=file_name)
        print(f"Data saved to {output_file}")

        pivoted_df = pivoted_df.pivot(index=["Area", "Area_Code", "Item", "Item_Code", "Year"],
                      columns="Element_Code",
                      values="Value")
        pivoted_df = pivoted_df.reset_index()
        pivoted_df.columns = pivoted_df.columns.astype("str")
        output_file_GFPM_cali = self.output_path / "FAO_DATA_as_GFPM_Calibration_Input.csv"
        pm.save_result(pivoted_df, path=str(self.output_path), file_name="FAO_DATA_as_GFPM_Calibration_Input")
        print(f"Data saved to {output_file_GFPM_cali}")

    def process(self):
        self.data = pm.read_original_data(input_path=self.input_path)
        self.reformat_data()
        self.save_reformatted_data()


if __name__ == "__main__":
    processor = FAODataProcessor()
    processor.process()