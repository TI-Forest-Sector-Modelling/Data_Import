import pandas as pd
from tqdm import tqdm
from pathlib import Path
import os
from Applications.Read_Data.ProcessManager import ProcessManager
pm = ProcessManager()

class FAODataProcessor:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = Path(output_path)
        self.data = None

    def read_original_data(self):
        try:
            self.data = pd.read_csv(self.input_path, encoding="latin-1")
            print("Data read successfully!")
        except FileNotFoundError:
            print(f"No data found in directory! Please ensure the file exists at: {self.input_path}")
            raise

    def reformat_data(self):
        if self.data is None:
            raise ValueError("No data to reformat. Please run `read_original_data` first.")

        print("\nStart reformatting original data to one vector")
        self.data = self.data.dropna(how="all", axis=1)

        col_values = self.data.filter(regex="^Y", axis=1).columns
        col_info = [col for col in self.data.columns if col not in col_values]

        temp_list_values = []
        temp_list_year = []
        temp_list_info = []

        for item in tqdm(self.data["Item Code"].unique(), desc="Processing items"):
            data_item = self.data[self.data["Item Code"] == item]
            for area in data_item["Area Code"].unique():
                data_area = data_item[data_item["Area Code"] == area]
                for element in data_area["Element Code"].unique():
                    data_element = data_area[data_area["Element Code"] == element]
                    data_element_info = data_element[col_info]
                    data_element_values = data_element[col_values]
                    data_element_transposed = data_element_values.transpose()

                    data_values = data_element_transposed.values.tolist()
                    data_year = data_element_values.columns.values.tolist()

                    temp_list_values.extend(data_values)
                    temp_list_year.extend(data_year)

                    temp_list_info_help = []
                    for info in data_element_info.values:
                        temp_list_info_help.extend([info] * len(col_values))

                    temp_list_info.extend(temp_list_info_help)

        print("Reformatting done")

        print("\nConcatenate reformatted Lists")
        reformatted_data = pd.concat(
            [pd.DataFrame(temp_list_info), pd.DataFrame(temp_list_year), pd.DataFrame(temp_list_values)], axis=1
        )

        col_names = ["Area_Code","Area_Code_M49","Area","Item_Code","Item","Element_Code","Element","Unit",
                     "Year","Value"]
        reformatted_data.columns = col_names
        reformatted_data = reformatted_data[["Area_Code", "Area", "Item_Code", "Item", "Element_Code", 
                                             "Element", "Unit", "Year", "Value"]]

        flag_data = pd.DataFrame(reformatted_data[reformatted_data["Year"].str[-1:] == "F"].Value)
        flag_data.columns = ["Flags"]

        reformatted_data = reformatted_data[reformatted_data["Year"].str[-1:] != "F"]
        reformatted_data = reformatted_data[reformatted_data["Year"].str[-1:] != "N"]

        self.data = pd.concat([reformatted_data.reset_index(drop=True), flag_data.reset_index(drop=True)], axis=1)
        self.data["Year"] = self.data["Year"].str.replace("Y", "")
        print("Concatenation complete")

    def save_reformatted_data(self, file_name: str = "FAO_DATA_as_vector"):
        """Save the reformatted data to the output path."""
        if self.data is None:
            raise ValueError("No data to save. Please process the data first.")
        
        self.data["Area_Code"] = self.data["Area_Code"].astype("int64", copy=False)
        self.data["Item_Code"] = self.data["Item_Code"].astype("int64", copy=False)
        self.data["Year"] = self.data["Year"].astype("int64", copy=False)

        self.data = self.data[["Area_Code", "Item_Code", "Element_Code", "Year", "Value"]]

        output_file = self.output_path / f"{file_name}.csv"
        pm.save_result(self.data, path=str(self.output_path), file_name=file_name)
        print(f"Data saved to {output_file}")

    def process(self):
        self.read_original_data()
        self.reformat_data()
        self.save_reformatted_data()


if __name__ == "__main__":
    INPUTPATH = r"E:\Data_Official_Reports\FAOStat\Forestry_E_All_Data.csv"
    OUTPUTPATH = Path(__file__).parent.parent.parent / "Output"

    processor = FAODataProcessor(input_path=INPUTPATH, output_path=str(OUTPUTPATH))
    processor.process()