from pathlib import Path

src_path = Path(__file__).parent.parent.parent

BACI_INPUT_FOLDER = src_path / r"data/baci_hs02_data_bulk"
FAO_INPUT_FILE = src_path / r"data/faostat_data_bulk/Forestry_E_All_Data.csv"
FRA_INPUT_FILE = src_path / r"data/fra_data_bulk/FRA_Years_2026-03-25.csv"
WDI_INPUT_FILE = src_path / r"data/wdi_data_bulk/WDICSV.csv"

url_wdi = "https://databank.worldbank.org/data/download/WDI_CSV.zip"
url_wdi_gdp_update = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json"
url_wdi_pop_update = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json"


url_faostat = "https://bulks-faostat.fao.org/production/Forestry_E_All_Data.zip"
url_faostat_update = "http://fenixservices.fao.org/faostat/static/bulkdownloads/datasets_E.xml"

url_baciHS02 = "https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS02_V"
url_baciHS02_update = "https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37"

# FRA url will probibly change in next version
url_fra = (
    "https://fra-data.fao.org/api/file/bulk-download"
    "?assessmentName=fra"
    "&countryIso=WO"
    "&cycleName=2025"
    "&includeClimaticDomain=undefined"
)

zip_path = src_path / r"data/Zip_Files/"
data_path = "FSMDataImport/data/"

fao_download_path = src_path  / r"data\faostat_data_bulk\Forestry_E_All_Data.csv"
wdi_download_path = src_path  / r"data\wdi_data_bulk\WDICSV.csv"
add_info_path = src_path  / r"Input/additional_info"
output_path = src_path  / r"Output"
folder_calibration_data = "Calibration_Data"

metadata_path = r"data/metadata.json"