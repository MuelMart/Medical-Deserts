import numpy as np
import pandas as pd
import os
import sqlite3
#This script reads in the Centers for Medicare & Meidcaid Services using their API.
csv = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/6fdc4567-4ae7-5d31-8adc-adeb7a629787/download?format=csv")

#Open db connection
db = "C:\\Users\\Sam\\OneDrive - Georgia Institute of Technology\\CSE 6242 - Visual and Data Analytics\\Project Resources\\Medical-Deserts\\project_data.sqlite"
conn = sqlite3.connect(db)

#Read to sqlite
csv.to_sql('DOCTORS', con = conn, if_exists = 'replace')

#Close conncetion
conn.close()

