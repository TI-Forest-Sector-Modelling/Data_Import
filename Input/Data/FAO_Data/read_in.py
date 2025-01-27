import pandas as pd
import numpy as np
from  tqdm import tqdm
import os
import time
from itertools import product
import matplotlib.pyplot as plt
from enum import Enum
import datatable as dt
import pyarrow
import fastparquet
from pathlib import Path

#DATAPATH = os.path.abspath(__file__)
DATAPATH = Path(__file__).parent.absolute().resolve()
print(DATAPATH)

class user_input(Enum):
    read_new_data = False
    subset_by_country = False
    country_name = "Europe"
    subset_by_country_code = False
    country_code_name = 79
    subset_by_commodity = False
    commodity_name= "Wood-based panels"
    subset_by_commodity_code = False
    commodity_code_name = 1861
    subset_by_year_min = True
    year_min = 1990
    subset_by_year_max = True
    year_max = 2025

    show_plot = False
    x_axis = "Year"
    y_axis = "Production"
    plot_title = "Production"

    print_results_to_excel = False
    print_results_to_csv = False
    user_output_name = "Results"
    user_output_excel_sheet_name = "Results"

def create_user_output(data: pd.DataFrame):
    excel_title = user_input.user_output_name.value + ".xlsx"
    csv_title = user_input.user_output_name.value + ".csv"
    if user_input.print_results_to_excel.value == True:
        writer = pd.ExcelWriter(excel_title, engine="xlsxwriter")
        data.to_excel(writer, sheet_name = user_input.user_output_excel_sheet_name.value, index=False)
        writer.save()
    if user_input.print_results_to_csv.value == True:
        data.to_csv(csv_title, index=False)

def subset_sample(data: pd.DataFrame):
    if user_input.subset_by_country.value:
        data = data[data["Area"].isin([user_input.country_name.value])]
    if user_input.subset_by_country_code.value:
        data = data[data["Area_Codes"].isin([user_input.country_code_name.value])]
    if user_input.subset_by_commodity.value:
        data = data[data["Item"] == user_input.commodity_name.value]
    if user_input.subset_by_commodity_code.value:
        data = data[data["Item_Codes"] == user_input.commodity_code_name.value]
    if user_input.subset_by_year_min.value:
        data = data[data["Year"] >= user_input.year_min.value]
    if user_input.subset_by_year_max.value:
        data = data[data["Year"] <= user_input.year_max.value]
    return data

def sort_sample(data: pd.DataFrame):
    data = data.sort_values(by = ["Area_Codes", "Item_Codes", "Year"], ascending = True)
    return data

def read_original_data():
    try:
        data = pd.read_csv(str(DATAPATH) + "\\Forestry_E_All_Data.csv", encoding = "latin-1")
        #data = dt.fread(str(DATAPATH) + "\\Forestry_E_All_Data.csv").to_pandas()
        data.info()
        print("read-in prcess done!")
    except FileNotFoundError:
        print("No data found in directory! Please download data bulk from FAOSTat to this directoy: " + os.path.abspath(os.getcwd()))
    return data

def reformatting():
    print("\nStart reformatting original data to one vector")
    data = pd.DataFrame(read_original_data())
    data = data.dropna(how= "all", axis=1)
    print(data)
    data.info()
    col_values = data.filter(regex = '^Y', axis = 1).columns
    col_info = [columns for columns in data.columns if columns not in col_values]
    temp_list_values = []
    temp_list_year = []
    temp_list_info = []
    for item in tqdm(data["Item Code"].unique()):
        data_item = data[data["Item Code"] == item]
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
                    help_info = [0] * len(col_values)
                    for i in range(len(col_values)):
                        help_info[i] = info
                    temp_list_info_help.extend(help_info)
                temp_list_info.extend(temp_list_info_help)
    print("Reformatting done")
    print("\nConcatenate reformated Lists")
    data_reformatted = pd.concat([pd.DataFrame(temp_list_info),pd.DataFrame(temp_list_year),pd.DataFrame(temp_list_values)], axis = 1)
    col_names = ["Area_Code", "Area_Code_M49", "Area", "Item_Code", "Item", "Element_Code", "Element", "Unit", "Year", "Value"]
    data_reformatted.columns = col_names
    data_reformatted = data_reformatted[["Area_Code", "Area", "Item_Code", "Item", "Element_Code", "Element", "Unit", "Year", "Value"]]
    flag_data = pd.DataFrame(data_reformatted[data_reformatted['Year'].str[-1:]=='F'].Value)
    flag_data.columns = ["Flags"]
    data_reformatted = data_reformatted[data_reformatted['Year'].str[-1:]!='F']
    data_reformatted = data_reformatted[data_reformatted['Year'].str[-1:]!='N']
    data_reformatted = pd.concat([data_reformatted.reset_index(drop=True), flag_data.reset_index(drop=True)], axis = 1)
    data_reformatted.Year = data_reformatted.Year.str.replace("Y", "")
    return data_reformatted

def complete_data(data: pd.DataFrame):
    data_complete = pd.DataFrame(list(product(data.Area_Code.unique(), data.Item_Code.unique(), data.Year.unique())))
    data_complete.columns = ["Area_Codes", "Item_Codes", "Years"]
    return data_complete

def reformatting_columns(data: pd.DataFrame):
    print("\nStart reformatting with element as columns")
    data_all = complete_data(data)
    data_all_copy = data_all
    for element in tqdm(data.Element.unique()):
        data_element = data[data.Element == element].reset_index(drop = True)
        data_element = data_all_copy.merge(data_element,
                                            how = "left", 
                                            left_on = ["Area_Codes", "Item_Codes", "Years"], 
                                            right_on =["Area_Code", "Item_Code", "Year"]
                                            )
        data_element = data_element[["Value","Flags"]]
        data_element.columns = [str(element),"Flags"]
        data_all = pd.concat([data_all, data_element],axis = 1)
    print(data_all)
    data_all.columns = ["Area_Code",  "Item_Code", "Year",
                        "Import_Value", "Flags_IV",
                        "Export_Value", "Flags_EV",
                        "Production", "Flags_P",
                        "Import_Quantity", "Flags_IQ",
                        "Export_Quantity", "Flags_EQ"]
    print("Reformatting done\n")
    return data_all

def build_additional_info_item(data: pd.DataFrame):
    item_list = []
    item_code_list = []
    for item_code in data["Item_Code"].unique():
        data_item = data[data["Item_Code"] == item_code]
        item = data_item["Item"][0:1]
        item_codes = data_item["Item_Code"][0:1]
        item_code_list.extend(item_codes)
        item_list.extend(item)
    item_code_series = pd.DataFrame(item_code_list, columns = ["Item_Codes"])
    item_series = pd.DataFrame(item_list, columns = ["Item"])
    item_df = pd.concat([item_code_series, item_series], axis = 1)
    return item_df

def build_additional_info_area(data: pd.DataFrame):
    area_list = []
    area_code_list = []
    for area_code in data["Area_Code"].unique():
        data_area = data[data["Area_Code"] == area_code]
        area = data_area["Area"][0:1]
        area_codes = data_area["Area_Code"][0:1]
        area_code_list.extend(area_codes)
        area_list.extend(area)
    area_code_series = pd.DataFrame(area_code_list, columns = ["Area_Codes"])
    area_series = pd.DataFrame(area_list, columns = ["Area"])
    area_df = pd.concat([area_code_series, area_series], axis = 1)
    return area_df

def build_additional_info_element(data: pd.DataFrame):
    element_list = []
    element_code_list = []
    element_unit_list = []
    for element_code in data["Element_Code"].unique():
        data_element = data[data["Element_Code"] == element_code]
        element = data_element["Element"][0:1]
        element_codes = data_element["Element_Code"][0:1]
        element_units = data_element["Unit"][0:1]
        element_code_list.extend(element_codes)
        element_list.extend(element)
        element_unit_list.extend(element_units)
    element_code_series = pd.DataFrame(element_code_list, columns = ["Element_Codes"])
    element_series = pd.DataFrame(element_list, columns = ["Element"])
    element_unit_series = pd.DataFrame(element_unit_list, columns = ["Unit"])
    element_df = pd.concat([element_code_series, element_series, element_unit_series], axis = 1)   
    return element_df

def write_additional_info(additional_info_item: pd.DataFrame, additional_info_area: pd.DataFrame, additional_info_element: pd.DataFrame):
    additional_info_item.to_pickle(str(DATAPATH) + "\\Item_Info.pkl")
    additional_info_area.to_pickle(str(DATAPATH) + "\\Area_Info.pkl")
    additional_info_element.to_pickle(str(DATAPATH) + "\\Element_Info.pkl")

def add_additioanl_info(additional_info_item: pd.DataFrame, additional_info_area: pd.DataFrame, data_complete: pd.DataFrame):
    data_complete = data_complete.merge(additional_info_item[["Item_Codes", "Item"]],
                                        how = "left", 
                                        left_on = ["Item_Code"], 
                                        right_on =["Item_Codes"]
                                        )
    data_complete = data_complete.merge(additional_info_area[["Area_Codes", "Area"]],
                                        how = "left", 
                                        left_on = ["Area_Code"], 
                                        right_on =["Area_Codes"]
                                        )
    data_complete = data_complete[["Area_Codes", "Area", "Item_Codes", "Item", "Year",
                                     "Import_Value", "Export_Value", "Production", "Import_Quantity", 
                                     "Export_Quantity"]] # "Unit"
    return data_complete

def ResultWriter(data_all: pd.DataFrame, csv_name: str, parquet_name: str):
    data_all.to_csv(str(DATAPATH) + "\\" + csv_name)
    data_all.to_parquet(str(DATAPATH) + "\\" + parquet_name)

def plot_data(data: pd.DataFrame):
    if user_input.show_plot.value:
        name_plot = user_input.plot_title.value + " for " + user_input.commodity_name.value
        data.plot.scatter(x=user_input.x_axis.value, y=user_input.y_axis.value, title = name_plot)
        #plt.xlim([-1000000, 10000000])
        plt.show()

def start_process(new_path: bool = False, set_path_to: str = ""):
    """Generate starting time annd set directory
    """
    global start_time
    start_time = time.time()
    if new_path:
        path = set_path_to
    else:
        path = os.path.abspath(os.getcwd())
    os.chdir(path)

def main_process():
    if user_input.read_new_data.value:
        data = reformatting()
        data_reformatted = reformatting_columns(data)
        additional_info_item = build_additional_info_item(data)
        additional_info_area = build_additional_info_area(data)
        additional_info_element = build_additional_info_element(data)
        write_additional_info(additional_info_item, additional_info_area, additional_info_element)
        data_reformatted = add_additioanl_info(additional_info_item, additional_info_area, data_reformatted)
        ResultWriter(data_reformatted, 
                     "Forestry_E_All_Data_reformatted.csv",
                     "Forestry_E_All_Data_reformatted.parquet")
    else:
        try:
            data_reformatted = pd.read_parquet(str(DATAPATH) + "\\Forestry_E_All_Data_reformatted.parquet")
            additional_info_item = pd.read_pickle(str(DATAPATH) + "\\Item_Info.pkl")
            additional_info_area = pd.read_pickle(str(DATAPATH) + "\\Area_Info.pkl")
            additional_info_element = pd.read_pickle(str(DATAPATH) + "\\Element_Info.pkl")
        except FileNotFoundError:
            print("Area_Info.pkl, Element_Info.pkl Item_Info.pkl and Forestry_E_All_Data_reformatted.parquet not found")
          
    data_reformatted.Area_Codes = data_reformatted.Area_Codes.astype('int64', copy=False)
    data_reformatted.Item_Codes = data_reformatted.Item_Codes.astype('int64', copy=False)
    data_reformatted.Year = data_reformatted.Year.astype('int64', copy=False)
    data_reformatted = data_reformatted[["Area", "Area_Codes", "Item", "Item_Codes", "Year", "Production", "Import_Quantity", "Import_Value", "Export_Quantity", "Export_Value"]]
    
    return data_reformatted

def end_process():
    end_time = time.time()
    print("This is the end!")
    print("--- %s seconds ---" % round((end_time - start_time),2))

def replace_na(data: pd.DataFrame):
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.replace([np.nan], 0, inplace=True)
    return data

def add_price(data: pd.DataFrame):
    export_price = data.Export_Value / (data.Export_Quantity / 1000)
    data["Export_Price"] = export_price
    import_price = data.Import_Value / (data.Import_Quantity / 1000)
    data["Import_Price"] = import_price
    weighted_price = (data.Import_Value + data.Export_Value) / ((data.Import_Quantity + data.Export_Quantity) / 1000)
    data["Weighted_Price"] = weighted_price.round(2)
    data = replace_na(data)
    return data

def add_consumption(data: pd.DataFrame):
    consumption = data.Production - data.Export_Quantity + data.Import_Quantity
    data["Consumption"] = consumption
    data = replace_na(data)
    return data

def downcasting(data: pd.DataFrame):
    data.Area = data.Area.astype("category")
    data.Area_Codes  = data.Area_Codes.astype("int32")
    data.Item  = data.Item.astype("category")
    data.Item_Codes = data.Item_Codes.astype("int32")
    data.Year = data.Year.astype("int16")
    data.Production = data.Production.astype("float32")
    data.Import_Quantity = data.Import_Quantity.astype("float32")
    data.Import_Value = data.Import_Value.astype("float32")
    data.Export_Quantity = data.Export_Quantity.astype("float32")
    data.Export_Value = data.Export_Value.astype("float32")

def main():
    start_process()
    data = main_process()

    #examples how to work with the resulting data
    data = sort_sample(data)
    data = subset_sample(data)
    ResultWriter(data, 
                 "Forestry_subsetted_Data_reformatted.csv",
                 "Forestry_subsetted_reformatted.parquet")
    create_user_output(data)
    print(data)
    downcasting(data)
    data.info()
    plot_data(data)
    #end of exemples

    end_process()

main()