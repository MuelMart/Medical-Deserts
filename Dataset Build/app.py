from Geoprocessing import export_map
from Geoprocessing import pull_tract_data
from Geoprocessing import pull_tract_geometries
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import sqlite3
import folium
from folium import plugins



#Pull data
dbpath = "C:\\Users\\Sam\\OneDrive - Georgia Institute of Technology\\CSE 6242 - Visual and Data Analytics\\Project Resources\\Medical-Deserts\\project_data.sqlite"

@st.cache_data
def build_dataset(dbpath):
    tract_data = pull_tract_data(dbpath)
    geoms = pull_tract_geometries(dbpath)

    #Ensure GEOIDs are same type.
    tract_data['GEOID'] = tract_data['GEOID'].astype('string')
    geoms['GEOID'] = geoms['GEOID'].astype('string')

    #Join data
    join = pd.merge(geoms, tract_data, on = 'GEOID', how = 'right')

    return join

@st.cache_data
def get_states(_join):
    #Get states
    states = [a for a in set(join['state'])]
    states.sort()

    return states

#Get data
join = build_dataset(dbpath)
states = get_states(join)


if __name__ == "__main__":


    st.title('Doctor Deserts')
    state = st.selectbox("Select a state:", states)

    #Generate map
    with st.spinner("Generating Map..."):
        map = export_map(join, state_abb = state)
        folium_static(map)
    


