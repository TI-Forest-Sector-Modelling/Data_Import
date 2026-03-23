from pathlib import Path

BACI_INPUT_FOLDER = r"E:\Data_Official_Reports\BACI"
FAO_INPUT_FILE = r"E:\Data_Official_Reports\FAOStat\Forestry_E_All_Data.csv"
WDI_INPUT_FILE = r"E:\Data_Official_Reports\WDI\WDICSV.csv"
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