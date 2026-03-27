from src.core.querries.querry_calibration import query_calibration_input
from src.core.querries.querry_armington import query_armington
from src.core.import_data.data_download import DataDownload, bulk_dict
from src.Input.Dictionaries.hscodes import timba_commodity_list
from src.core.processes.ProcessManager import ProcessManager
from src.core.processes.read_FAO import FAODataProcessor
from src.core.processes.read_WDI import WDIDataProcessor
from src.core.processes.read_BACI import BACIProcessor
import src.Input.path_names.paths as p
from src.core.processes.build_metadata import MetadataManager
from pathlib import Path
from datetime import datetime

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
    INPUTPATH = Path(__file__).parent  / p.fao_download_path
    OUTPUTPATH = Path(__file__).parent / p.output_path
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
    INPUTPATH = Path(__file__).parent  / p.wdi_download_path
    OUTPUTPATH = Path(__file__).parent / p.output_path
    wdp = WDIDataProcessor(
        input_path=INPUTPATH, 
        output_path=str(OUTPUTPATH)
    )
    wdp.main_process()
    pm.end_process()

def calibration_data():
    pm.start_process()
    ADD_INFO_PATH = Path(__file__).parent / p.add_info_path
    OUTPUTPATH = Path(__file__).parent / p.output_path / p.folder_calibration_data
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

def check_version():
    print("Latest update:")
    wdi_latest = WDIDataProcessor().check_wdi_updates()
    fao_latest = FAODataProcessor().check_fao_updates()
    baci_latest, baci_version = BACIProcessor().check_baci_version()

    wdi_info_list = [
        p.url_wdi,
        p.WDI_INPUT_FILE,
        wdi_latest,
    ]

    baci_info_list = [
        p.url_baciHS02,
        p.BACI_INPUT_FOLDER,
        baci_latest,
    ]

    fao_info_list = [
        p.url_faostat,
        p.FAO_INPUT_FILE,
        fao_latest,
    ]

    fra_info_list = [
        p.url_fra,
        p.FRA_INPUT_FILE,
        "",
    ]

    update_dict={
        "WDI": wdi_info_list,
        "FAO": fao_info_list,
        "FRA": fra_info_list,
        "BACI": baci_info_list,
    }
    print(update_dict)

    metadata = MetadataManager()

    for key, value in update_dict.items():
        source = key
        dataset = key
        url = value[0]
        local_file = value[1]

        entry = metadata.create_entry(
            source=source,
            dataset=dataset,
            download_url=url,
            local_file=local_file,
            dataset_last_update=value[2],
        )

        metadata.update(entry)
        metadata.save()


if __name__ == "__main__":
    check_version()
    #data_download()
    #read_fao_data()
    #read_wdi_data()
    #calibration_data()
    #armington_data()