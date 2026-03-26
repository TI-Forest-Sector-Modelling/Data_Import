import os
import json
import hashlib
from datetime import datetime
from src.Input.path_names.paths import metadata_path


class MetadataManager:
    """
    Manages metadata for downloaded datasets (e.g. WDI, FAO, FRA, BACI).

    This class handles:
    - Loading and saving metadata as JSON
    - Creating standardized metadata entries
    - Updating entries (with optional version check)
    - Computing file hashes for integrity/version tracking
    """

    def __init__(self, path=metadata_path):
        self.path = path
        self.metadata = self._load()

    def _load(self):
        """
        Load metadata from JSON file.

        Returns:
            dict: Existing metadata if file exists, otherwise empty dictionary.
        """
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        """
        Save current metadata dictionary to JSON file.
        """        
        with open(self.path, "w") as f:
            json.dump(self.metadata, f, indent=4)

    def _get_file_hash(self, filepath):
        """
        Compute SHA-256 hash of a file.

        Args:
            filepath (str): Path to the file.

        Returns:
            str or None: SHA-256 hash as hex string, or None if file does not exist.
        """        
        if not filepath or not os.path.exists(filepath):
            return None

        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def create_entry(
        self,
        source,
        dataset,
        download_url,
        local_file=None,
        dataset_last_update=None
        ):
        """
        Create a standardized metadata entry for a dataset.

        Args:
            source (str): Data source (e.g. 'WDI', 'FAO', 'FRA', 'BACI').
            dataset (str): Dataset name or identifier.
            download_url (str): URL used to download the dataset.
            local_file (str, optional): Local file path of the downloaded dataset.
            dataset_last_update (str, optional): Last update date of the dataset (from source).

        Returns:
            dict: Metadata entry containing dataset information and file properties.
        """
        file_size = os.path.getsize(local_file) if local_file and os.path.exists(local_file) else None
        sha256 = self._get_file_hash(local_file)

        return {
            "source": source,
            "dataset": dataset,
            "download_url": download_url,
            "local_file": local_file,
            "downloaded_at": datetime.now().isoformat(),
            "dataset_last_update": dataset_last_update,
            "file_size_bytes": file_size,
            "sha256": sha256
        }

    def update(self, entry):
        """
        Insert or overwrite a metadata entry unconditionally.

        Args:
            entry (dict): Metadata entry created by `create_entry`.
        """
        key = f"{entry['source']}_{entry['dataset']}"
        self.metadata[key] = entry

    def update_if_newer(self, entry):
        """
        Optional function: Update metadata entry only if the dataset is newer.

        Compares the 'dataset_last_update' field of the existing entry
        with the new one. If the new entry is not newer, no update is performed.

        Args:
            entry (dict): Metadata entry created by `create_entry`.
        """
        key = f"{entry['source']}_{entry['dataset']}"

        if key in self.metadata:
            old_date = self.metadata[key].get("dataset_last_update")
            new_date = entry.get("dataset_last_update")

            if old_date and new_date and new_date <= old_date:
                print(f"No update needed for {key}")
                return

        print(f"Metadata updates saved for {key}")
        self.metadata[key] = entry