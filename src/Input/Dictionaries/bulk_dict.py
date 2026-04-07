import src.Input.path_names.paths as paths
import src.Input.parameters.user_input as bulks
import json
from pathlib import Path

def bulk_dict():
    json_path = Path(__file__).parent.parent.parent / paths.metadata_path
    print(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    baci_url = data["BACI_BACI"]["download_url"]

    return {
        bulks.wdi_bulk_name:paths.url_wdi,
        bulks.faostat_bulk_name:paths.url_faostat,
        bulks.fra_bulk_name:paths.url_fra,
        bulks.baci_bulk_name:baci_url,
    }