import requests
import zipfile
from pathlib import Path
import shutil
import FSMDataImport.Input.path_names.paths as paths
from FSMDataImport.Input.Dictionaries.dicts import bulk_dict

class DataDownload:
    def __init__(self, url, bulk_name):
        self.url = url
        self.bulk_name = bulk_name
    
    def download(self):
        """
        Download the file from the given URL and save it locally.
        """
        print(f"Beginn to download: {self.bulk_name}")
        paths.zip_path.mkdir(parents=True, exist_ok=True)

        self.output_path = paths.zip_path / Path(self.bulk_name)

        response = requests.get(self.url, stream=True)
        response.raise_for_status()

        with open(self.output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"{self.bulk_name} download is finished!")

    def extract_zip(self):
        """
        Extract the downloaded ZIP file to the target directory.
        """
        extraction_path = Path(paths.data_path + self.bulk_name[:-4])
        extraction_path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.output_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_path)

        print(f"{self.bulk_name} is extracted!")
    
    def cleanup(self):
        """
        Remove the downloaded ZIP file after extraction.
        """
        if self.output_path.exists():
            self.output_path.unlink()
    
    def main(self):
        """
        Execute full workflow: download, extract, and clean up.
        """
        self.download()
        self.extract_zip()
        self.cleanup()

if __name__ == "__main__":
    for bulk, url in bulk_dict().items():
        dd = DataDownload(
            url=url,
            bulk_name=bulk
        )
        dd.main()
    