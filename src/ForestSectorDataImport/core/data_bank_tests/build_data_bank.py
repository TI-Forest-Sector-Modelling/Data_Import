import pandas as pd
import sqlite3

class build_db:
    def __init__(self, db_file_name: str, 
                 output_folder: str,
                 input_file: str):
        
        self.db_file_name = db_file_name
        self.output_folder = output_folder
        self.input_file = input_file
    
    def read_files(self):
        try:
            self.df = pd.read_parquet(self.input_file)
            print("Parquet-Datei erfolgreich geladen.")
        except Exception as e:
            print("Fehler beim Laden der Parquet-Datei:", e)
            exit()

    def create_db(self):
        conn = sqlite3.connect(self.output_folder + self.db_file_name)
        cursor = conn.cursor()

    def add_table(self):
        table_name = 'forestry_data'
        try:
            self.df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            print(f"Tabelle '{table_name}' erfolgreich in die SQLite-Datenbank eingefügt.")
        except Exception as e:
            print("Fehler beim Importieren der Daten in SQLite:", e)

    def close_db(self):
        self.conn.close()
        print(f"SQLite-Datenbank '{self.db_file_name}' wurde geschlossen.")

if __name__ == "__main__":
    pass
    #output_folder='E:\\P_Data_Import\\Data_Import\\Output\\'
    #input_file = 'E:\P_Data_Import\Data_Import\Output\FAO_DATA_as_vector.parquet'
    #db_file = 'datenbank.db'