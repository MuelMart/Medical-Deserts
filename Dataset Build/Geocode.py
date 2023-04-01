import censusgeocode as cg
from geopy.geocoders import ArcGIS
from geopy.extra.rate_limiter import RateLimiter
import sqlite3
import pandas as pd

def pull_data(dbpath):
    #First, define a function that pulls in doctor data and groups them by address.
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    #Query to group doctor location data by address
    query = """
    SELECT adrs_id, 
    CAST(org_pac_id AS TEXT) AS org_pac_id,
    (CASE WHEN org_pac_id IS NULL THEN CAST(npi AS TEXT) ELSE NULL END) AS npi,
    COALESCE(org_nm, lst_nm || ', ' || frst_nm) AS provider_name, adr_ln_1 || ', ' || cty ||', '|| st ||', '|| zip AS address,
    ln_2_sprs,
    COUNT(npi) AS num_clinicians 
    FROM DOCTORS
    GROUP BY adrs_id, org_pac_id
    """

    #Execute query to DF
    doc_locations_raw = pd.read_sql(query, con = conn)

    conn.close()

    return doc_locations_raw

#Geocode address
def geocode_df(geocode, df):
    df = df.copy()
    df['location'] = df['address'].apply(geocode)
    df['lat'] = df['location'].apply(lambda x: x.latitude)
    df['lon'] = df['location'].apply(lambda x: x.longitude)

    return df.drop('location', axis = 1)

#Write to db
def build_table(df, dbpath):
    conn = sqlite3.connect(dbpath)
    df.to_sql('DOCTORS_LOCATIONS', con = conn, if_exists = 'replace')
    conn.close


#Run this if you have a built geocoder and reference to sqlite db.
def main(dbpath, geocode):
    df = pull_data(dbpath)
    geocoded = geocode_df(geocode, df)
    build_table(geocoded, dbpath)