import pandas as pd
import numpy as np
import logging
from tqdm import tqdm
from pathlib import Path
from src.core.processes.ProcessManager import ProcessManager
from src.core.processes.read_BACI import BACIProcessor
from src.core.processes.read_FAO import FAODataProcessor
from src.core.processes.read_WDI import WDIDataProcessor
from src.Input.path_names.paths import BACI_INPUT_FOLDER, FAO_INPUT_FILE, WDI_INPUT_FILE, add_info_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DataProcessor:
    def __init__(self, output_path: Path):
        self.pm = ProcessManager()
        self.baci_input_folder = Path(BACI_INPUT_FOLDER)
        self.fao_input_file = Path(FAO_INPUT_FILE)
        self.wdi_input_file = Path(WDI_INPUT_FILE)
        self.output_path = Path(output_path)

    def read_BACI_data(self):
        """
        Process BACI trade data and save results.
        """
        logging.info("Begin processing BACI data...")
        add_info_path = Path(__file__).parent.parent / add_info_path
        processor = BACIProcessor(
            input_path=self.baci_input_folder, 
            output_path=self.output_path, 
            add_info_path=add_info_path
        )
        processor.process_data()

    def read_FAO_data(self):
        """
        Process FAO data and save results.
        """
        logging.info("Begin processing FAO data...")
        processor = FAODataProcessor(
            input_path=self.fao_input_file, 
            output_path=self.output_path
        )
        processor.process()

    def read_WDI_data(self):
        """
        Process WDI data and save results.
        """
        logging.info("Begin processing WDI data...")
        processor = WDIDataProcessor(
            input_path=self.wdi_input_file, 
            output_path=self.output_path
        )
        processor.main_process()

    def process(self, func):
        """
        Execute a processing function with logging and error handling.
        
        Args:
            func (callable): Processing function to execute.
        """
        self.pm.start_process()
        try:
            func()
        except Exception as e:
            logging.error(f"Fehler in {func.__name__}: {e}", exc_info=True)
        finally:
            self.pm.end_process()

    def run(self):
        """
        Run all data processing steps sequentially with progress tracking.
        """
        func_list = [self.read_BACI_data, self.read_FAO_data, self.read_WDI_data]
        for func in tqdm(func_list, desc="Processing datasets"):
            self.process(func)

if __name__ == "__main__":
    OUTPUT_FOLDER = Path(__file__).parent.parent.parent / "Output"
    processor = DataProcessor(output_path=OUTPUT_FOLDER)
    processor.run()