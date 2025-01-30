import sqlite3
import numpy as np
import pandas as pd

# Datenbank öffnen
conn = sqlite3.connect('E:\P_Data_Import\Data_Import\Output\datenbank.db')
cursor = conn.cursor()

def print_results(amount_of_data):
    # Tabelle anzeigen
    cursor.execute("SELECT * FROM forestry_data LIMIT " + str(amount_of_data))
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def one_vector():
    # Abfrage ausführen
    cursor.execute("SELECT Import_Value FROM forestry_data")
    result = cursor.fetchall()

    # Ergebnisse in ein NumPy-Array umwandeln
    vector = np.array([row[0] for row in result])
    print(pd.DataFrame(vector))

def main():
    print_results(5)
    #one_vector()

main()
conn.close()