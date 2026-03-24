from pathlib import Path

BACI_INPUT_FOLDER = r"src/data/baci_hs02_data_bulk/BACI"
FAO_INPUT_FILE = r"src/data/faostat_data_bulk/Forestry_E_All_Data.csv"
FRA_INPUT_FILE = r"src/data/fra_data_bulk/Forestry_E_All_Data.csv"
WDI_INPUT_FILE = r"src/data/wdi_data_bulk/WDICSV.csv"

url_wdi = "https://databank.worldbank.org/data/download/WDI_CSV.zip"
url_faostat = "https://bulks-faostat.fao.org/production/Forestry_E_All_Data.zip"
url_baciHS02 = "https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS02_V202601.zip"
url_fra = (
    "https://fra-data.fao.org/api/file/bulk-download"
    "?assessmentName=fra"
    "&countryIso=WO"
    "&cycleName=2025"
    "&includeClimaticDomain=undefined"
)

zip_path = Path("src/data/Zip_Files/")
data_path = "src/data/"