import requests
import zipfile
from pathlib import Path
import shutil
import src.Input.path_names.paths as paths
import src.Input.parameters.user_input as bulks

bulk_dict={
    bulks.wdi_bulk_name:paths.url_wdi,
    bulks.faostat_bulk_name:paths.url_faostat,
    bulks.fra_bulk_name:paths.url_fra,
    bulks.baci_bulk_name:paths.url_baciHS02,
}

class DataDownload:
    def __init__(self, url, bulk_name):
        self.url = url
        self.bulk_name = bulk_name
    
    def download(self):
        paths.zip_path.mkdir(parents=True, exist_ok=True)

        self.output_path = paths.zip_path / Path(self.bulk_name)

        response = requests.get(self.url, stream=True)
        response.raise_for_status()

        with open(self.output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"{self.bulk_name} download is finished!")

    def extract_zip(self):
        extraction_path = Path(paths.data_path + self.bulk_name[:-4])
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
    for bulk, url in bulk_dict.items():
        dd = DataDownload(
            url=url,
            bulk_name=bulk
        )
        dd.main()
    