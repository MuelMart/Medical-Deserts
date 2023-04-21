from Geoprocessing import export_map, geo_avg_fig, pull_tract_data, pull_tract_geometries, get_statedata, geo_clust_fig
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_folium import folium_static
import numpy as np
import argparse
import re

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

@st.cache_data
def read_geojson(gjson):
    return gpd.read_file(gjson,driver='GeoJSON')

@st.cache_data
def get_vars(data):
    return [a for a in data.columns if a != 'y_Pred']




if __name__ == "__main__":

    #Set arguments for demo data or full data
    parser = argparse.ArgumentParser(description='Set the mode for which the app will run.')
    parser.add_argument('mode', metavar='M', choices = ['full','demo'], type=str, nargs=1,
                        help='The mode for the app, either full or demo')
    args = parser.parse_args()
    mode = args.mode[0]

    #If mode is demo
    if mode == 'demo':
        #Load in demo data for app
        join = read_geojson('demodata.geojson')
        states = get_states(join)
        states.reverse()

    else:
        #Get data from sqlitedb
        #Set dbpath
        dbpath = "appdata.sqlite"
        join = build_dataset(dbpath)
        states = get_states(join)

    st.title('Medical :orange[Deserts]')
    st.header('A Snapshot of Healthcare Access in America')

    #Special message for demo mode
    if mode == 'demo':
        st.markdown('''
        >Medical deserts are defined as areas where individuals live “...over 25 km (i.e., more than a 20-min drive) from the closest hospital” (Di Novi 2020).
        In order to better understand Medical deserts and where they persist, select a state from the list below and explore the map.
        The map displays all the **census tracts** within the state, colored by the number of doctors that are within 25 kilometers of said tract.
        Please note that you are currently using the Demo version, which only displays states for the states AL, MS, GA, SC, and NC.
        If you would like access to the full version, please contact the authors below.
        ''')

    else:
        st.markdown('''
        >Medical deserts are defined as areas where individuals live “...over 25 km (i.e., more than a 20-min drive) from the closest hospital” (Di Novi 2020).
        In order to better understand Medical deserts and where they persist, select a state from the list below and explore the map.
        The map displays all the **census tracts** within the state, colored by the number of doctors that are within 25 kilometers of said tract.
        ''')

    #State dropdown
    state = st.selectbox("Select a state:", states)

    #Generate map
    with st.spinner("Generating Map..."):
        m,m2 = export_map(join, state_abb = state)
        folium_static(m)

    st.header('State Statistics: {}'.format(state))
    
    with st.spinner("Generating State Statistics..."):
        #Generate bar chart of state and national averages.
        st.markdown("##### Average Number of Clinicians near Tract")
        st.pyplot(geo_avg_fig(join, state))
        st.caption('The average number of doctors within 25 kilometers of a census tract. {} state average compared to national average'.format(state))

        #Get state data
        stdata = get_statedata(join, state)

        #Dashboard for state and national doc per tract averages
        c1, c2 = st.columns(2)
        c1.metric('State Average', np.round(np.mean(stdata['Number of Clinicians'])))
        c2.metric('National Average', np.round(np.mean(join['total_clinicians'])))
        
        st.markdown("##### State Demographic Indicators")
        st.dataframe(stdata.drop('y_Pred', axis = 1).describe().drop(['count'],axis = 0))
        st.caption("""The above table shows summary statistics for several socio-economic variables from the American Community survey. These variables are captured at the tract level, and aggregated within the selected state.""")

    st.header('Medical Desert Risk: {}'.format(state))
    st.markdown('''
    >In addition to understanding where Medical Deserts are physically located, 
    we also utilized Gaussian Mixture Model Clustering (GMM) to identify two distinct tract typologies: <span style="color:#7aab65">**High Vulnerability**</span> and <span style="color:#8a5eb5">**Low Vulnerability**</span>.
    ''',unsafe_allow_html=True)

    st.markdown('''
    <span style="color:#8a5eb5">**Low Vulnerability**</span> tracts are tracts that are less likely to experience some form of inadequate healthcare access.
    <span style="color:#7aab65">**High Vulnerability**</span> tracts are tracts that are likely to experience some form of inadequate healthcare access.
    \nThey fall within a distribution that posesses the following means:
    ''',unsafe_allow_html = True)
    

    #Cluster means
    means = [[4.07790549e-01, 4.81188578e+00, 8.23502017e+00, 1.40751118e+01, 
            7.09270635e+04, 2.16909260e+05, 4.61561122e+00, 2.06238667e+01,
            4.41009002e+01, 5.64096647e+00, 5.86666517e+02],
            [4.38705613e-01, 7.22199139e+00, 9.76779292e+00, 1.21828744e+01,
            8.07092102e+04, 4.41795907e+05, 1.39214607e+01, 4.76717763e+01,
            5.16785026e+01, 7.85865053e+00, 3.00901008e+03]]
    means = [[round(a,2) for a in m] for m in means]
    mean_vars = ['Income Disparity (Gini Index)',
                 'Unemployment Rate',
                 'Percent Uninsured Population',
                 'Percent Disabled Population',
                 'Median Household Income (USD)',
                 'Median Home Price (USD)',
                 'Percent Households with No Vehicle',
                 'Percent Non-White Population',
                 'Percent Rent Burdened Population',
                 'Percent Single Parent Households',
                 'Number of Clinicians']
    means_df = pd.DataFrame(means, columns = mean_vars)
    means_df.index = ['Low Vulnerability','High Vulnerability']
    st.dataframe(means_df)


    
    with st.spinner("Generating Risk Map..."):
        #Now display the cluster map
        folium_static(m2)

    st.header('Vulnerability Statistics: {}'.format(state))

    #Select a variable to display
    vars = get_vars(stdata)
    var = st.selectbox("Select a Socio-Economic Indicator:", vars)

    with st.spinner("Generating Risk Statistics..."):

        #Return bar chart
        st.pyplot(geo_clust_fig(stdata, var))
        st.caption('This shows the average value across all census tracts within {}, facetted by High Vulnerable tracts and Low Vulnerable tracts'.format(state))

        mean_vuln = np.round(np.mean(stdata[stdata['y_Pred'] == 1][var].dropna()),3)
        mean_nvuln = np.round(np.mean(stdata[stdata['y_Pred'] == 0][var].dropna()),3)
        s1, s2 = st.columns(2)
        if re.match('^Percent', var) != None:
            s1.metric('High Vulnerability', mean_vuln, delta = '{} %'.format(np.round(mean_vuln - mean_nvuln,2)))
        else:
            s1.metric('High Vulnerability', mean_vuln, delta = np.round(mean_vuln - mean_nvuln,2))
        st.caption('Here, the delta value represents the difference between High Vulnerability tracts and Low Vulnerability tracts')

        s2.metric('Low Vulnerability', mean_nvuln)




    st.text('Samuel Martinez, Romy Patel, Rutika Karande, Harry Sharp')
    st.text('Data for this tool was sourced from the American Community Survey \nand the Centers for Medicare & Medicaid Services')
    


