import pandas as pd
import sqlite3

# Pfad zur hochgeladenen Parquet-Datei
parquet_file = 'E:\P_Data_Import\Data_Import\Output\FAO_DATA_as_vector.parquet'

# Parquet-Datei mit pandas einlesen
try:
    df = pd.read_parquet(parquet_file)
    print("Parquet-Datei erfolgreich geladen.")
except Exception as e:
    print("Fehler beim Laden der Parquet-Datei:", e)
    exit()

# SQLite-Datenbank erstellen/verknüpfen
db_file = 'datenbank.db'  # Name der SQLite-Datenbank
conn = sqlite3.connect('E:\\P_Data_Import\\Data_Import\\Output\\' + db_file)
cursor = conn.cursor()

# Tabelle in SQLite schreiben
table_name = 'forestry_data'
try:
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Tabelle '{table_name}' erfolgreich in die SQLite-Datenbank eingefügt.")
except Exception as e:
    print("Fehler beim Importieren der Daten in SQLite:", e)

# Verbindung schließen
conn.close()
print(f"SQLite-Datenbank '{db_file}' wurde geschlossen.")