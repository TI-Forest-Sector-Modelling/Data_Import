from pathlib import Path
import pandas as pd
from ForestSectorDataImport.core.import_data.data_distribution import DataImporter
from ForestSectorDataImport.Input.Dictionaries.fao_codes import element_dict
import ForestSectorDataImport.Input.Dictionaries.hscodes as codes# commodity_list, aggregated_commodity_list, timba_commodity_list
import ForestSectorDataImport.Input.path_names.paths as p# output_path, add_info_path
from ForestSectorDataImport.core.processes.ProcessManager import ProcessManager

class query_armington:
    def __init__(self, commodity_list:list):
        self.pm = ProcessManager(commodity_list=commodity_list)
        self.ADD_INFO_PATH = p.add_info_path
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
        Keep original HS codes and add mapped FAO code as extra column.
        """

        baci_data = baci_data.reset_index(drop=True)

        # neue Spalte statt Überschreiben
        baci_data["FAOCode"] = baci_data["HSCode"].map(hs_to_fao_code_dict)

        # nur gemappte behalten
        baci_data = baci_data.dropna(subset=["FAOCode"]).reset_index(drop=True)

        # optional int
        baci_data["FAOCode"] = baci_data["FAOCode"].astype(int)

        aggregated_baci_data = baci_data.groupby(
            [
                'Year',
                'Reporter_Code',
                'Partner_Code',
                'HSCode',      # original bleibt
                'FAOCode'      # zusätzlicher Schlüssel
            ],
            as_index=False
        ).sum()

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
            left_on=['Year', 'Partner_Code', 'FAOCode'],
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

        armington_data = armington_data.rename(columns={
            "FAOCode": "FAO_Code"
        })

        print(armington_data)

        self.pm.save_result(
            path=p.output_path, 
            data=armington_data,
            file_name="armington_data"
        )

if __name__ == "__main__":
    qa = query_armington(
        commodity_list=codes.aggregated_commodity_list
    )
    qa.main_process()