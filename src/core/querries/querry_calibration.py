from pathlib import Path
import pandas as pd
from src.core.import_data.data_distribution import DataImporter
from src.Input.Dictionaries.gfpm_input_file_codes import input_codes

class query_calibration_input:
    def __init__(self, output_path: Path, add_info_path: Path):
        self.ADD_INFO_PATH = add_info_path
        self.output_path = output_path
        self.file_list = ["FAO_DATA_as_GFPM_Calibration_Input.parquet",
                          "WDI_DATA_as_vector.parquet"]

    def data_import(self):
        importer = DataImporter(
            file_list=self.file_list,
            output_folder=self.output_path
        )
        return importer.main_process()

    def process_fao_data(self, fao_data):
        fao_data["Production"] = fao_data["5510"].combine_first(fao_data["5516"])
        fao_data["Import Quantity"] = fao_data["5610"].combine_first(fao_data["5616"])
        fao_data["Export Quantity"] = fao_data["5910"].combine_first(fao_data["5916"])
        fao_data["Import Value"] = fao_data["5622"]
        fao_data["Export Value"] = fao_data["5922"]
        fao_data = fao_data[["Area","Area_Code","Item","Item_Code",
                             "Year","Production","Import Quantity",
                             "Import Value","Export Quantity","Export Value"]]
        fao_data["Year"]=fao_data["Year"].astype("int")
        fao_data = fao_data[fao_data["Year"]>=1992]
        fao_data=fao_data.sort_values(by=['Year', 'Area_Code'], ascending=[False, True])
        return fao_data
    
    def output_path_generator(self):
        if not self.output_path.exists():
            self.output_path.mkdir(parents=True, exist_ok=True)

    def filter_and_save(self, data:pd.DataFrame):
        self.output_path_generator()
        print("\nFolder to save calibration information is:" , self.output_path)
        for keys in input_codes:
            filtered_data=data[data["Item_Code"]==input_codes[keys]].reset_index(drop=True)
            filtered_data.to_csv(self.output_path / f"{keys}.csv", index=False)
            print(f"saved {keys}.csv")

    def deflator_table(self,data:pd.DataFrame):
        self.output_path_generator()
        deflator = data[data["Indicator_Code"]=="NY.GDP.DEFL.ZS"]
        us_deflator = deflator[deflator["WDI_ISO3"]=="USA"]
        new_base = us_deflator.loc[us_deflator["Year"] == 2023, "Value"].iloc[0]
        us_deflator = us_deflator.assign(new_base=us_deflator["Value"] / new_base * 100)
        us_deflator = us_deflator.rename(columns={
            "WDI_ISO3": "Country Code",
            "Year": "Time Name",
            "Value": "GDP deflator (base 2015)",
            "new_base": "GDP deflator (base 2023)"
        })
        us_deflator["Country Name"] = us_deflator["Country Code"]
        us_deflator=us_deflator[[
            "Time Name",
            "Country Name",
            "Country Code",
            "GDP deflator (base 2015)",
            "GDP deflator (base 2023)"
        ]]

        us_deflator.to_excel(
            self.output_path / "GDPDeflatorUS.xlsx", 
            index=False
        )

        print("saved", "GDPDeflatorUS.xlsx")

    def gdp_population_table(self,data:pd.DataFrame):
        self.output_path_generator()
        wdi_filter = [
            "NY.GDP.MKTP.CD",
            "SP.POP.TOTL"
        ]

        gdppop = data[data["Indicator_Code"].isin(wdi_filter)].reset_index(drop=True)
        gdppop = gdppop.pivot(
            index=["WDI_ISO3", "Year"], 
            columns="Indicator_Code", 
            values="Value"
        )
        gdppop=gdppop.reset_index()

        gdppop = gdppop.rename(columns={
            "WDI_ISO3": "Country Code",
            "Year": "Time Name",
            "NY.GDP.MKTP.CD": "GDP (current US$)",
            "SP.POP.TOTL": "Population, total"
        })

        gdppop["Country Name"] = gdppop["Country Code"]
        gdppop=gdppop[["Time Name","Country Name","Country Code","GDP (current US$)","Population, total"]]
        gdppop.to_excel(self.output_path / "GDPPopulation.xlsx", index=False) 
        print("saved", "GDPPopulation.xlsx")

    def main_process(self):
        data_dict = self.data_import()
        fao_data = self.process_fao_data(fao_data = data_dict["FAO_data"])
        self.filter_and_save(data=fao_data)
        wdi_data=data_dict["WDI_data"]
        self.deflator_table(data=wdi_data)
        self.gdp_population_table(data=wdi_data)
        
if __name__ == "__main__":
    qc = query_calibration_input()
    qc.main_process()