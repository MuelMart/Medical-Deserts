from Geoprocessing import export_map, geo_avg_fig, pull_tract_data, pull_tract_geometries
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import numpy as np



#Pull data
dbpath = "appdata.sqlite"

@st.cache_data
def build_dataset(dbpath):
    tract_data = pull_tract_data(dbpath)
    geoms = pull_tract_geometries(dbpath)

    #Ensure GEOIDs are same type.
    tract_data['GEOID'] = tract_data['GEOID'].astype('string')
    geoms['GEOID'] = geoms['GEOID'].astype('string')

    #Join data
    join = pd.merge(geoms, tract_data, on = 'GEOID', how = 'right')
    #Filter out empty geometries
    output = join[join['geometry'].is_empty == False]

    return output

@st.cache_data
def get_states(_join):
    #Get states
    states = [a for a in set(join['state'])]
    states.sort()

    return states


if __name__ == "__main__":

    #Get data
    join = build_dataset(dbpath)
    states = get_states(join)


    st.title('Medical :orange[Deserts]')
    st.header('A Snapshot of Healthcare Access in America')
    st.markdown('''
    >Medical deserts are defined as areas where individuals live “...over 25 km (i.e., more than a 20-min drive) from the closest hospital” (Di Novi 2020).
    In order to better understand Medical deserts and where they persist, select a state from the list below and explore the map.
    The map displays all the **census tracts** within the state, colored by the number of doctors that are within 25 kilometers of said tract.
    ''')
    state = st.selectbox("Select a state:", states)

    #Generate map
    with st.spinner("Generating Map..."):
        map = export_map(join, state_abb = state)
        folium_static(map)

    st.header('State Statistics: {}'.format(state))
    
    with st.spinner("Generating State Statistics..."):
        #Generate bar chart of state and national averages.
        st.markdown("##### Average Number of Clinicians near Tract")
        st.pyplot(geo_avg_fig(join, state))
        st.caption('The average number of doctors within 25 kilometers of a census tract. {} state average compared to national average'.format(state))

        #Get state data
        stdata = join[join['state'] == state].drop(['geometry', 'index', 'lat', 'lon'], axis=1)

        #Dashboard for state and national doc per tract averages
        c1, c2 = st.columns(2)
        c1.metric('State Average', np.round(np.mean(stdata['total_clinicians'])))
        c2.metric('National Average', np.round(np.mean(join['total_clinicians'])))

        #Now display the tract aggregated vulnerability indicators
        #Initialize display dataframe
        display = pd.DataFrame()
        #Rename columns
        display['Number of Clinicians'] = stdata['total_clinicians']
        display['Median Household Income (USD)'] = stdata['MedianHouseholdIncomeE']
        display['Median Home Price (USD)'] = stdata['MedianHomePriceE']
        display['Income Disparity (Gini Index)'] = stdata['IncomeDisparityE']
        display['Unemployment Rate'] = stdata['UnemploymentRateE']
        display['Percent Uninsured Population'] = stdata['P_UninsuredE']
        display['Percent Disabled Population'] = stdata['P_WithADisabilityE']
        display['Percent Households with No Vehicle'] = stdata['P_NoVehicleAvailableE']
        display['Percent Non-White Population'] = stdata['P_NonWhiteE'] 
        display['Percent Rent Burdened Population'] = stdata['P_RentBurdenedE']
        display['Percent Single Parent Households'] = stdata['P_SingleParentHouseholdE']
        
        
        st.markdown("##### State Demographic Indicators")
        st.dataframe(display.describe().drop(['count'],axis = 0))
        st.caption("""The above table shows summary statistics for several socio-economic variables from the American Community survey. These variables are captured at the tract level, and aggregated within the selected state.""")



    st.text('Samuel Martinez, Romy Patel, Rutika Karande, Harry Sharp')
    st.text('Data for this tool was sourced from the American Community Survey \nand the Centers for Medicare & Medicaid Services')
    


