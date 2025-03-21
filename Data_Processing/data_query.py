from pathlib import Path
import pandas as pd
import openpyxl
from Data_Processing.import_data.data_distribution import DataImporter
from Input.Dictionaries.fao_codes import element_dict
from Input.Dictionaries.hscodes import commodity_list, aggregated_commodity_list, timba_commodity_list
from Input.Dictionaries.gfpm_input_file_codes import input_codes
from Data_Processing.Read_Data.ProcessManager import ProcessManager

class query_armington:
    def __init__(self, commodity_list:list):
        self.pm = ProcessManager(commodity_list=commodity_list)
        self.ADD_INFO_PATH = Path(__file__).parent.parent / "Input/additional_info"
        self.file_list = ["BACI_DATA_as_vector.parquet",
                          "FAO_DATA_as_vector.parquet",
                          "WDI_DATA_as_vector.parquet"]

    def data_import(self):
        importer = DataImporter(file_list=self.file_list)
        return importer.main_process()

    def process_fao_data(self, fao_data, country_dict, hs_to_fao_code_dict, element_dict):
        fao_data = fao_data.reset_index(drop=True)
        fao_data = self.pm.replace_column_data_with_dict(data=fao_data, mapping_dict=country_dict)

        value_list = list(set(hs_to_fao_code_dict.values()))
        fao_data = fao_data[fao_data["Item_Code"].isin(value_list)].reset_index(drop=True)

        fao_data = self.pm.replace_column_data_with_dict(data=fao_data, mapping_dict=element_dict, column_name="Element_Code")
        fao_data = fao_data.pivot(index=['Area_Code', 'Item_Code', 'Year'], columns='Element_Code', values='Value')
        return fao_data.reset_index().fillna(0)

    def process_baci_data(self, baci_data, hs_to_fao_code_dict):
        baci_data = baci_data.reset_index(drop=True)
        baci_data = self.pm.replace_column_data_with_dict(data=baci_data, mapping_dict=hs_to_fao_code_dict, column_name="HSCode")

        baci_data = baci_data[baci_data["HSCode"] <= 2000].reset_index(drop=True)
        aggregated_baci_data = baci_data.groupby(['Year', 'Reporter_Code', 'Partner_Code', 'HSCode'], as_index=False).sum()
        return aggregated_baci_data

    def merge_data(self, aggregated_baci_data, processed_fao_data):
        armington_data = pd.merge(aggregated_baci_data, processed_fao_data,
                                  left_on=['Year', 'Partner_Code', 'HSCode'],
                                  right_on=['Year', 'Area_Code', 'Item_Code'],
                                  how='left')
        
        armington_data.drop(columns=['Area_Code', 'Item_Code'], inplace=True)
        return armington_data

    def main_process(self):
        data_dict = self.data_import()

        country_dict = self.pm.read_additional_info(add_input_path=self.ADD_INFO_PATH)
        hs_to_fao_code_dict = self.pm.hs_to_fao_dict()

        processed_fao_data = self.process_fao_data(data_dict["FAO_data"], 
                                                   country_dict, 
                                                   hs_to_fao_code_dict, 
                                                   element_dict)
        
        aggregated_baci_data = self.process_baci_data(data_dict["BAC_data"], hs_to_fao_code_dict)
        armington_data = self.merge_data(aggregated_baci_data, processed_fao_data)
        print(armington_data)
        armington_data.columns =['Year', 'Partner_Code', 'Reporter_Code', 'HSCode', 'Value', 'Quantity',
                                 'Export_Quantity', 'Export_Value', 'Import_Quantity', 'Import_Value','Production']
        print(armington_data)
        OUTPUT_PATH = Path(__file__).parent.parent / "Output"
        self.pm.save_result(path=OUTPUT_PATH, data=armington_data,file_name="armington_data")

class query_calibration_input:
    def __init__(self):
        self.ADD_INFO_PATH = Path(__file__).parent.parent / "Input/additional_info"
        self.file_list = ["FAO_DATA_as_GFPM_Calibration_Input.parquet",
                          "WDI_DATA_as_vector.parquet"]

    def data_import(self):
        importer = DataImporter(file_list=self.file_list)
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
        return fao_data
    
    def output_path_generator(self):
        self.output_path = Path(__file__).parent.parent / "Output" / "Calibration_Data"
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
        us_deflator=us_deflator[["Time Name","Country Name","Country Code","GDP deflator (base 2015)","GDP deflator (base 2023)"]]
        us_deflator.to_excel(self.output_path / "GDPDeflatorUS.xlsx", index=False)
        print("saved", "GDPDeflatorUS.xlsx")

    def gdp_population_table(self,data:pd.DataFrame):
        self.output_path_generator()
        wdi_filter = ["NY.GDP.MKTP.CD","SP.POP.TOTL"]
        gdppop = data[data["Indicator_Code"].isin(wdi_filter)].reset_index(drop=True)
        gdppop = gdppop.pivot(index=["WDI_ISO3", "Year"], columns="Indicator_Code", values="Value")
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
    # qa = query_armington(commodity_list=timba_commodity_list)
    # qa.main_process()

    qc = query_calibration_input()
    qc.main_process()