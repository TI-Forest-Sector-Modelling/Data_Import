from src.core.querries.querry_calibration import query_calibration_input
from src.core.querries.querry_armington import query_armington
from src.core.import_data.data_download import DataDownload, bulk_dict
from src.Input.Dictionaries.hscodes import timba_commodity_list
from src.core.processes.ProcessManager import ProcessManager
from src.core.processes.read_FAO import FAODataProcessor
from src.core.processes.read_WDI import WDIDataProcessor
from src.core.processes.read_BACI import BACIProcessor
from src.Input.path_names.paths import output_path, fao_download_path, wdi_download_path , add_info_path, folder_calibration_data
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

def check_version():
    print("Latest update:")
    wdi_latest = WDIDataProcessor().check_wdi_updates()
    fao_latest = FAODataProcessor().check_fao_updates()
    baci_latest, baci_version = BACIProcessor().check_baci_version()
    update_dict={
        "WDI": wdi_latest,
        "FAO": fao_latest,
        "BACI": baci_latest
    }
    print(update_dict)
    print(baci_version)
    
    # manager = MetadataManager()

    # source = "FRA"
    # dataset = "FRA 2025"
    # url = "https://fra-data.fao.org/.../FRA_Years_2025.zip"
    # local_file = "data/fra.zip"

    # # 👉 Schritt 1: Datum vom Server holen
    # latest_date = "2026-01-30"  # z. B. aus Last-Modified

    # # 👉 Schritt 2: Prüfen ob Update nötig
    # if manager.should_update(source, dataset, latest_date):

    #     # 👉 Schritt 3: Download (deine Funktion)
    #     download_file(url, local_file)

    #     # 👉 Schritt 4: Metadata erstellen
    #     entry = manager.create_entry(
    #         source=source,
    #         dataset=dataset,
    #         download_url=url,
    #         local_file=local_file,
    #         dataset_last_update=latest_date
    #     )

    #     # 👉 Schritt 5: speichern
    #     manager.update(entry)
    #     manager.save()


if __name__ == "__main__":
    check_version()
    #data_download()
    #read_fao_data()
    #read_wdi_data()
    #calibration_data()
    #armington_data()