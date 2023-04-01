import pandas as pd
import sqlite3

def build_table(db_path):
    #This script reads in the Centers for Medicare & Meidcaid Services using their API.
    csv = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/6fdc4567-4ae7-5d31-8adc-adeb7a629787/download?format=csv")

    #Open db connection
    #Update to your local path
    conn = sqlite3.connect(db_path)

    #Read to sqlite
    csv.to_sql('DOCTORS_RAW', con = conn, if_exists = 'replace')

    #Close conncetion
    conn.close()

#Dedupe and clean data
#Select only family practice / internal medicine doctors. Dedupe them by their address ID and clinician ID.
def dedupe_data(db_path):

    #Open connection
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    #Drop the table if it exists
    cur.execute('DROP TABLE IF EXISTS DOCTORS')

    #Create the table of doctor practicioners
    query = """
    CREATE TABLE DOCTORS AS 
    SELECT * FROM DOCTORS_RAW
    WHERE (pri_spec = 'FAMILY PRACTICE' OR pri_spec = 'INTERNAL MEDICINE')
	AND	ROWID IN(
        SELECT MIN(ROWID)
        FROM DOCTORS_RAW
        GROUP BY npi, adrs_id
    )
    """

    cur.execute(query)

    #Close connection
    conn.close()

#Main function for doint the whole thing
def main(db_path):
    build_table(db_path)
    dedupe_data(db_path)