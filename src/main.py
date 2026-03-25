from src.core.querries.querry_calibration import query_calibration_input
from src.core.querries.querry_armington import query_armington
from src.core.import_data.data_download import DataDownload, bulk_dict
from src.Input.Dictionaries.hscodes import timba_commodity_list
from src.core.processes.ProcessManager import ProcessManager
from src.core.processes.read_FAO import FAODataProcessor
from src.core.processes.read_WDI import WDIDataProcessor
from src.Input.path_names.paths import output_path, fao_download_path, wdi_download_path , add_info_path, folder_calibration_data
from pathlib import Path

pm = ProcessManager()

def data_download():
    for bulk, url in bulk_dict.items():
        pm.start_process()
        dd = DataDownload(
            url=url,
            bulk_name=bulk
        )
        dd.main()
        pm.end_process()

def read_fao_data():
    pm.start_process()
    INPUTPATH = Path(__file__).parent  / fao_download_path
    OUTPUTPATH = Path(__file__).parent / output_path
    print(INPUTPATH)
    print(OUTPUTPATH)
    fdp = FAODataProcessor(
        input_path=INPUTPATH, 
        output_path=OUTPUTPATH
    )
    fdp.process()
    pm.end_process()

def read_wdi_data():
    pm.start_process()
    INPUTPATH = Path(__file__).parent  / wdi_download_path
    OUTPUTPATH = Path(__file__).parent / output_path
    wdp = WDIDataProcessor(
        input_path=INPUTPATH, 
        output_path=str(OUTPUTPATH)
    )
    wdp.main_process()
    pm.end_process()

def calibration_data():
    pm.start_process()
    ADD_INFO_PATH = Path(__file__).parent / add_info_path
    OUTPUTPATH = Path(__file__).parent / output_path / folder_calibration_data
    qc = query_calibration_input(
        output_path=OUTPUTPATH,
        add_info_path=ADD_INFO_PATH,
    )
    qc.main_process()
    pm.end_process()

def armington_data():
    pm.start_process()
    qa = query_armington(
        commodity_list=timba_commodity_list
    )
    qa.main_process()
    pm.end_process()


if __name__ == "__main__":
    data_download()
    read_fao_data()
    read_wdi_data()
    calibration_data()
    #armington_data()