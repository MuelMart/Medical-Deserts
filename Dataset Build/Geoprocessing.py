import pandas as pd
import geopandas as gpd
import numpy as np
import pyproj
import sqlite3
import folium

#Pull doc location data
def pull_doc_data(dbpath):
    conn = sqlite3.connect(dbpath)
    df = pd.read_sql('SELECT adrs_id, org_pac_id, npi, provider_name, num_clinicians, CAST(lat AS TEXT) AS lat, CAST(lon AS TEXT) AS lon FROM DOCTORS_LOCATIONS', con = conn)
    conn.close()

    return df

#Pull tract location data
def pull_tract_data(dbpath):
    conn = sqlite3.connect(dbpath)
    df = pd.read_sql('SELECT * FROM TRACTS', con = conn)
    conn.close()

    return df

#Get tract geometries
def pull_tract_geometries(dbpath):
    conn = sqlite3.connect(dbpath)
    gdf = gpd.read_postgis("SELECT * FROM TRACT_GEOMETRIES", con = conn, geom_col = 'geometry')
    conn.close()
    
    return gdf

#Function to calculate the number of doctors within 25km.
def calc_docs_within_25km(doc_data, tract_data, geoms):

    #Create a 25 km buffer around tracts
    buffer_geom = geoms.copy().to_crs('ESRI:102009')
    buffer_geom['geometry'] = buffer_geom['geometry'].buffer(25000)

    #Convert doctor location data to spatial dataframe
    doc_data_geom = doc_data.copy()
    points = gpd.points_from_xy(doc_data_geom['lon'], doc_data_geom['lat'])
    doc_data_geom = gpd.GeoDataFrame(doc_data_geom, geometry = points, crs="EPSG:4326").to_crs("ESRI:102009")

    #Perform spatial intersection with the buffer data
    geo_join = buffer_geom.sjoin(doc_data_geom, how = 'left', predicate = 'contains')

    #Group geo_join by GEOID and sum up number of clinicians
    geo_join_clean = pd.DataFrame(geo_join.copy().drop(columns = 'geometry')).groupby('GEOID')['num_clinicians'].sum().sort_values(ascending = False)

    #Join with tract data
    tract_w_num = tract_data.join(geo_join_clean, on = 'GEOID', how = 'left').rename(columns = {'num_clinicians':'total_clinicians'})

    return tract_w_num

#Takes dbpath, output from calc_docs_within_25km
def execute_sql(dbpath, tract_table):
    conn = sqlite3.connect(dbpath)
    tract_table.to_sql('TRACTS', con = conn, if_exists = 'replace')
    conn.close()
    


#Func to create and export folium maps
def export_map(tract_data, geoms, geo_join_clean, export_path, state_abb = None):

    #Get tracts for state or entire country, then filter with geometry
    if state_abb != None:
        ga_tracts = tract_data[tract_data.state == state_abb]['GEOID']
        ga_geoms = geoms[geoms['GEOID'].isin(ga_tracts)].to_crs('EPSG:4269')

    else:
        ga_geoms = geoms.to_crs('EPSG:4269')

    #Create a map for tract geometry
    #Get centroid point
    bounds = ga_geoms.dissolve().centroid

    #Create a map for number of docters per tract
    docs_per_tract = ga_geoms.join(geo_join_clean, on = 'GEOID', how = 'left')
    #Get thresholds
    intervals = docs_per_tract['num_clinicians'].describe()
    thresholds = [0,1,intervals['25%'],intervals['50%'],intervals['75%'],intervals['max']]

    #Create map from bounding box
    docs_per_tract_map = folium.Map(location = [bounds[0].y, bounds[0].x], zoom_start = 5)

    #Create chloropleth
    folium.Choropleth(
        geo_data = docs_per_tract.set_index('GEOID')['geometry'].to_json(),
        data = docs_per_tract,
        columns = ['GEOID','num_clinicians'],
        key_on = 'feature.id',
        fill_color = 'RdYlGn',
        fill_opacity = 0.5,
        line_opacity = 0,
        bins = thresholds,
        legend_name = 'Number of Clinicians within 25km of Tract'
    ).add_to(docs_per_tract_map)

    docs_per_tract_map.save(export_path + '\{}_tracts.html'.format(state_abb))


def main(dbpath):

    doc_data = pull_doc_data(dbpath)
    geoms = pull_tract_geometries(dbpath)
    tract_data = pull_tract_data(dbpath)

    #perform geoprocessing
    tract_table = calc_docs_within_25km(doc_data, tract_data, geoms)

    execute_sql(dbpath, tract_table)

main(dbpath)

