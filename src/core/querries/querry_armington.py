from pathlib import Path
import pandas as pd
from src.core.import_data.data_distribution import DataImporter
from src.Input.Dictionaries.fao_codes import element_dict
from src.Input.Dictionaries.hscodes import commodity_list, aggregated_commodity_list, timba_commodity_list
from src.core.processes.ProcessManager import ProcessManager

class query_armington:
    def __init__(self, commodity_list:list):
        self.pm = ProcessManager(commodity_list=commodity_list)
        self.ADD_INFO_PATH = Path(__file__).parent.parent.parent / "Input/additional_info"
        self.file_list = [
            "BACI_DATA_as_vector.parquet",
            "FAO_DATA_as_vector.parquet",
            "WDI_DATA_as_vector.parquet"
        ]

    def data_import(self):
        """
        Load all required datasets using the DataImporter.
        
        Returns:
            dict: Dictionary containing imported datasets.
        """
        importer = DataImporter(
            file_list=self.file_list
        )
        return importer.main_process()

    def process_fao_data(
            self, 
            fao_data, 
            country_dict, 
            hs_to_fao_code_dict, 
            element_dict
            ):
        """
        Clean and reshape FAO data:
        - Map country and element codes
        - Filter relevant items
        - Pivot to wide format
        
        Returns:
            pd.DataFrame: Processed FAO dataset.
        """

        fao_data = fao_data.reset_index(drop=True)
        fao_data = self.pm.replace_column_data_with_dict(
            data=fao_data, 
            mapping_dict=country_dict
        )

        value_list = list(set(hs_to_fao_code_dict.values()))
        fao_data = fao_data[fao_data["Item_Code"].isin(value_list)].reset_index(drop=True)

        fao_data = self.pm.replace_column_data_with_dict(
            data=fao_data, 
            mapping_dict=element_dict, 
            column_name="Element_Code"
        )

        fao_data = fao_data.pivot(
            index=[
                'Area_Code', 
                'Item_Code', 
                'Year'
            ], 
            columns='Element_Code', 
            values='Value'
        )

        return fao_data.reset_index().fillna(0)

    def process_baci_data(
            self, 
            baci_data, 
            hs_to_fao_code_dict
            ):
        """
        Clean and aggregate BACI trade data:
        - Map HS to FAO codes
        - Filter relevant codes
        - Aggregate trade flows
        
        Returns:
            pd.DataFrame: Aggregated BACI dataset.
        """
             
        baci_data = baci_data.reset_index(drop=True)
        baci_data = self.pm.replace_column_data_with_dict(
            data=baci_data, 
            mapping_dict=hs_to_fao_code_dict, 
            column_name="HSCode"
        )

        baci_data = baci_data[baci_data["HSCode"] <= 2000].reset_index(drop=True)
        aggregated_baci_data = baci_data.groupby(
            [
                'Year', 
                'Reporter_Code', 
                'Partner_Code', 
                'HSCode'
            ], 
            as_index=False).sum()
        
        return aggregated_baci_data

    def merge_data(
            self, 
            aggregated_baci_data, 
            processed_fao_data
            ):
        """
        Merge BACI data with FAO data.
        
        Returns:
            pd.DataFrame: Combined dataset for estimating armington elasticities.
        """  
        
        armington_data = pd.merge(
            aggregated_baci_data, 
            processed_fao_data,
            left_on=['Year', 'Partner_Code', 'HSCode'],
            right_on=['Year', 'Area_Code', 'Item_Code'],
            how='left'
        )
        
        armington_data.drop(
            columns=['Area_Code', 'Item_Code'], 
            inplace=True
        )

        return armington_data

    def main_process(self):
        """
        Run the full pipeline:
        - Import data
        - Process FAO and BACI datasets
        - Merge results
        - Save final dataset
        """
        
        data_dict = self.data_import()

        country_dict = self.pm.read_additional_info(
            add_input_path=self.ADD_INFO_PATH
        )
        hs_to_fao_code_dict = self.pm.hs_to_fao_dict()

        processed_fao_data = self.process_fao_data(
            data_dict["FAO_data"], 
            country_dict, 
            hs_to_fao_code_dict, 
            element_dict
        )
        
        aggregated_baci_data = self.process_baci_data(
            data_dict["BAC_data"], 
            hs_to_fao_code_dict
        )

        armington_data = self.merge_data(
            aggregated_baci_data, 
            processed_fao_data
        )

        armington_data.columns =[
            'Year', 
            'Partner_Code', 
            'Reporter_Code', 
            'HSCode', 
            'Value', 
            'Quantity',
            'Export_Quantity', 
            'Export_Value', 
            'Import_Quantity', 
            'Import_Value',
            'Production'
        ]

        OUTPUT_PATH = Path(__file__).parent.parent.parent / "Output"
        self.pm.save_result(path=OUTPUT_PATH, data=armington_data,file_name="armington_data")

if __name__ == "__main__":
    qa = query_armington(
        commodity_list=timba_commodity_list
    )
    qa.main_process()