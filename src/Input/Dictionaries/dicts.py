import src.Input.path_names.paths as paths
import src.Input.parameters.user_input as bulks
from src.core.processes.ProcessManager import ProcessManager

def bulk_dict():
    metadata = ProcessManager().call_metadata_json()
    baci_url = metadata["CEPII_BACI"]["download_url"]

    return {
        bulks.wdi_bulk_name:paths.url_wdi,
        bulks.faostat_bulk_name:paths.url_faostat,
        bulks.fra_bulk_name:paths.url_fra,
        bulks.baci_bulk_name:baci_url,
    }

data_dict = {
    "WDI": "WorldBank",
    "BACI": "CEPII",
    "FRA": "FAO",
    "FAO": "FAO"
}