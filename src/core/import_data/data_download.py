import requests
import zipfile
from pathlib import Path
import shutil
from src.Input.path_names.paths import url_faostat, url_fra, zip_path, data_path
from src.Input.parameters.user_input import fra_bulk_name, faostat_bulk_name

class DataDownload:
    def __init__(self, zip_path, url, bulk_name):
        self.zip_path = Path(zip_path)
        self.url = url
        self.bulk_name = bulk_name
    
    def download(self):
        self.zip_path.mkdir(parents=True, exist_ok=True)

        self.output_path = self.zip_path / Path(self.bulk_name)

        response = requests.get(self.url, stream=True)
        response.raise_for_status()

        with open(self.output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"{self.bulk_name} download is finished!")

    def extract_zip(self):
        extraction_path = Path(data_path + self.bulk_name[:-4])
        extraction_path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.output_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_path)

        print(f"{self.bulk_name} is extracted!")
    
    def cleanup(self):
        if self.output_path.exists():
            self.output_path.unlink()
    
    def main(self):
        self.download()
        self.extract_zip()
        self.cleanup()

if __name__ == "__main__":
    fao_dd = DataDownload(
        zip_path=zip_path, 
        url=url_faostat,
        bulk_name=faostat_bulk_name
    )
    fao_dd.main()

    fra_dd = DataDownload(
        zip_path=zip_path, 
        url=url_fra,
        bulk_name=fra_bulk_name
    )
    fra_dd.main()
    