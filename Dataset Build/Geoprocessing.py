import pandas as pd
import geopandas as gpd
import numpy as np
import pyproj
import sqlite3
import folium
from geopy.geocoders import Nominatim
from folium import plugins
import matplotlib.pyplot as plt

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
def export_map(joined_data, geolocator= Nominatim(user_agent='app'), export_path = None, state_abb = None):

    docs_per_tract = joined_data.copy()

    #Get tracts for state or entire country, then filter with geometry
    if state_abb != None:
        data = docs_per_tract[docs_per_tract.state == state_abb].to_crs('EPSG:4269')
        bounds = geolocator.geocode(state_abb + ', USA')

        x = bounds[1][1]
        y = bounds[1][0]

    else:
        data = docs_per_tract.to_crs('EPSG:4269')
        bounds = data.dissolve().centroid
        
        x = bounds[0].x
        y = bounds[0].y

    #Get thresholds
    intervals = docs_per_tract['total_clinicians'].describe(percentiles = [0.2,0.4,0.6,0.8])
    thresholds = [0,1,intervals['20%'],intervals['40%'],intervals['60%'],intervals['80%'],intervals['max']]

    #Create map from bounding box
    m = folium.Map(location = [y,x], zoom_start = 5)

    data_json = data.to_json()

    #Create chloropleth
    gj = folium.Choropleth(
        geo_data = data_json,
        data = data.drop('geometry',axis=1),
        columns = ['GEOID','total_clinicians'],
        key_on = 'feature.properties.GEOID',
        fill_color = 'RdYlGn',
        fill_opacity = 0.6,
        line_opacity = 0,
        bins = thresholds,
        legend_name = 'Number of Clinicians within 25km of Tract',
        highlight = True,
        tooltip = None
    ).add_to(m)

    #Create tooltip
    folium.GeoJsonTooltip(fields = ['NAME', 'total_clinicians'], aliases = ['Name', 'Docs within 25km']).add_to(gj.geojson)

    if export_path != None:
        m.save(export_path + '\{}_tracts.html'.format(state_abb))

    return m

def geo_avg_fig(data,geo,type = 'state'):
    #Filter for da geography of interest
    filt = data[data[type] == geo]

    #Get avg docs per tract in state
    s_avg = np.mean(filt['total_clinicians'])
    n_avg = np.mean(data['total_clinicians'])
    labels = ['State Average','National Average']

    fig = plt.figure()
    plt.style.use('dark_background')
    plt.bar(labels, [s_avg,n_avg], color = ['#4287f5','#b6bfcf'])
    plt.rc('font', family='IBM Plex Sans')
    plt.xticks(weight = 'bold')
    
    return fig



def main(dbpath):

    doc_data = pull_doc_data(dbpath)
    geoms = pull_tract_geometries(dbpath)
    tract_data = pull_tract_data(dbpath)

    #perform geoprocessing
    tract_table = calc_docs_within_25km(doc_data, tract_data, geoms)

    execute_sql(dbpath, tract_table)

