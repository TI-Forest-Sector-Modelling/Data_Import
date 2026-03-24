from src.core.querries.querry_calibration import query_calibration_input
from src.core.querries.querry_armington import query_armington
from src.core.import_data.data_download import DataDownload, bulk_dict
from src.Input.Dictionaries.hscodes import timba_commodity_list

def data_download():
    for bulk, url in bulk_dict.items():
        dd = DataDownload(
            url=url,
            bulk_name=bulk
        )
    dd.main()

def calibration_data():
    qc = query_calibration_input()
    qc.main_process()

def armington_data():
    qa = query_armington(commodity_list=timba_commodity_list)
    qa.main_process()


if __name__ == "__main__":
    data_download()
    armington_data()