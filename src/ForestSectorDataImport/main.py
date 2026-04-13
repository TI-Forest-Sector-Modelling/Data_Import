from ForestSectorDataImport.core.querries.querry_calibration import query_calibration_input
from ForestSectorDataImport.core.querries.querry_armington import query_armington
from ForestSectorDataImport.core.import_data.data_download import DataDownload
from ForestSectorDataImport.Input.Dictionaries.dicts import bulk_dict
from ForestSectorDataImport.Input.Dictionaries.hscodes import timba_commodity_list
from ForestSectorDataImport.core.processes.ProcessManager import ProcessManager
from ForestSectorDataImport.core.processes.read_FAO import FAODataProcessor
from ForestSectorDataImport.core.processes.read_WDI import WDIDataProcessor
from ForestSectorDataImport.core.processes.read_BACI import BACIProcessor
import ForestSectorDataImport.Input.path_names.paths as p
from ForestSectorDataImport.core.processes.build_metadata import MetadataManager

pm = ProcessManager()

def data_download():
    """
    Download data from BACI, WDI, FAOStat, and FRA, and save the extracted files to src/data.
    Note:
    Downloading the data, especially from BACI, can take a considerable amount of time (up to about one hour).
    Data from WDI and FAOStat typically download within a few seconds to a minute.
    """
    for bulk, url in bulk_dict().items():
        pm.start_process()
        dd = DataDownload(
            url=url,
            bulk_name=bulk
        )
        dd.main()
        pm.end_process()


def calibration_data():
    """
    Process FAO and WDI data for TiMBA Calibration files.
    Files can be found at src/Output/Calibration_Data.
    """
    processes = [
        FAODataProcessor().process,
        WDIDataProcessor().main_process,
        query_calibration_input().main_process,
    ]

    for process in processes:
        pm.start_process()
        process()
        pm.end_process()

def armington_data():
    """
    Process BACI, FAO and WDI data for files used in bilateral trade analysis.
    Files can be found at ...
    (work in progress)
    """
    pm.start_process()
    qa = query_armington(
        commodity_list=timba_commodity_list
    )
    qa.main_process()
    pm.end_process()

def check_version_build_metadata():
    """
    Check if a newer version of each data source is available online (except of FRA data).
    Build Meta data file with the informations about newer versions.
    """
    bp = BACIProcessor().check_baci_version()
    pm = ProcessManager()
    dsd = pm.build_data_source_dict(
        wdi_latest=WDIDataProcessor().check_wdi_updates(),
        fao_latest=FAODataProcessor().check_fao_updates(),
        baci_latest=bp[0],
        baci_version=bp[1],
    )
    MetadataManager().generate_meta_data(data_source_dict=dsd)
    metadata = pm.call_metadata_json()

    for key, entry in metadata.items():
        if pm.update_check(key=key):
            print(f"Update required for {key}")
        else:
            print(f"{key} is up to date!")


if __name__ == "__main__":
    check_version_build_metadata()
    #data_download()
    #calibration_data()
    #armington_data()