# A Spatial and Computational Analysis of Medical Deserts
This repository serves as the codebase for our CSE6242 final project.
>The objective of our research is to utilize an analytical approach to identify and understand the characteristics of medical deserts. We plan to achieve this task by leveraging American Community Survey 5-year Estimate data alongside Centers for Medicare & Medicaid Services data. With this data, we intend to calculate the number of family practice doctor’s offices within a 25 km radius of each tract centroid in the country. A clustering model will be applied to the data to identify discrete groups that exhibit similar demographic characteristics, socioeconomic characteristics (e.g. tract poverty rate, median household income, etc.), as well as healthcare facility access. Additionally, the researchers will employ a regularized regression model to identify which socioeconomic / demographic characteristics are most important in determining the number of doctors within a 25 km radius of a tract. The final product will come in the form of an interactive map which displays which tracts are most vulnerable with respect to healthcare access alongside additional information regarding the demographic profile of said tracts. The hope is that this project can provide a new perspective to understanding the mechanisms through which inequity can perpetuate the hinderance of medical access.

## Table of Contents
[Data Dictionary](#data-dictionary)  
[Accessing the App](#accessing-the-app)

## Data Dictionary
The dataset is housed in a SQLite database, which contains the following tables:

- TRACTS
- DOCTORS_RAW
- DOCTORS
- DOCTORS_LOCATIONS

### TRACTS
Contains census tract data. Sourced from [American Community Survey 5-Year Estimates](https://www.census.gov/data/developers/data-sets/acs-5year.html) for the 2021 year.

**GEOID**  
Unique identifier for each census tract (I.e 02013000100)

**NAME**  
Census tract name (I.e Census Tract 1, Aleutians East Borough, Alaska)

**state**  
State abbreviation (I.e OH)

**IncomeDisparityE**  
ACS Var B19083_001. This is the [Gini Coefficient](https://en.wikipedia.org/wiki/Gini_coefficient) for a census tract.

**UnemploymentRateE**  
ACS Var S2301_C04_001. The percentage of adults 16 years or older who are not in the labor force for a census tract.

**P_UninsuredE**  
ACS Var S2701_C05_001. The percentage of a census tract's population that does not have health insurance.

**P_WithADisabilityE**  
ACS Var S1810_C03_001. The percentage of tract population that has a disability of some sort.

**MedianHouseholdIncomeE**  
ACS Var S1901_C01_012. The Median Household Income for a census tract.

**MedianHomePriceE**  
ACS Var DP04_0089. The Median Home Price for a census tract. 

**P_NoVehicleAvailableE**  
ACS Var DP04_0058P. The percentage of households in a tract that do not have a vehicle.

**P_NonWhiteE**  
100 - ACS Var DP05_0037P. The percentage of tract population that is non-white.

**P_RentBurdenedE**  
ACS Var DP04_0141P + ACS Var DP04_0142P. The percentage of households in a tract that are rent burdened (paying >30% of their income on rent).

**P_SingleParentHouseholdE**  
ACS Var DP02_0007P + ACS Var DP02_0011P. The percentage of households in a tract that are headed by a single parent.

**total_clinicians**  
The total number of *Internal Medicine* or *Family Practice* doctors within 25km of the census tract. Data was aggregated from **DOCTORS_LOCATIONS**.

### DOCTORS_RAW  
This is an export of the Centers for Medicare and Medicaid (CMS) [National Downloadable File](https://data.cms.gov/provider-data/dataset/mj5m-pzi6). Please consult the [data dicitionary](https://data.cms.gov/provider-data/sites/default/files/data_dictionaries/physician/DOC_Data_Dictionary.pdf) on the CMS Website.

### DOCTORS
A filtered copy of the **DOCTORS_RAW** table, which contains data for only *Internal Medicine* and *Family Practice* clinicians.

### DOCTORS_LOCATIONS
Contains the geocoded locations of all practices from the **DOCTORS** table.

**adrs_id**  
Unique identifier for the address of the practice.

**org_pac_id**  
Unique identifer for the practice organization. Is NULL for individual private practice clinicians (since they are not part of an organization)

**npi**  
Unique identifier for individual private practice clinicians. Is NULL for organizations.

**provider_name**  
Name of the practice organization or private practice clinician.

**address**  
Practice address in the following format: addr_ln_1, cty, st, zip

**ln_2_sprs**  
Field indicating if the addr_ln_2 is unreliable.

**num_clinicians**  
Either the sum of all *Internal Medicine* or *Family Practice* clinicians in the specified organization. Or 1 for a individual private practice clinician.

**lat**  
The WGS84 (EPSG 4326) latitude of the practice.

**lon**  
The WGS84 (EPSG 4326) longitude of the practice.

### TRACT_GEOMETRIES
Contains the geometries for every tract in the country. Stored using the [spatialite](https://www.gaia-gis.it/fossil/libspatialite/index) SQLite extension.

**GEOID**  
Unique tract identifier.

**geometry**  
ST feature geometry for the census tract (EPSG 4269).

## Accessing the App
To utilize the app, please adhere to the following steps:

1. Download the app package from [Dataset Build](https://github.com/MuelMart/Medical-Deserts/tree/main/Dataset%20Build) folder of this repo.
2. Extract package contents locally.
2. Make sure you have an installation of [anaconda](https://anaconda.org/) on your machine.
3. Open the anaconda prompt, and change the directory to the folder containing the app package contents. `cd Path/To/My/Directory`
4. Paste the following into the anaconda prompt: `initialize_env.bat`. This will intialize all package dependencies for the app.
5. Once the environment is created, paste the following into the anaconda prompt: `app.bat`. This will launch a demo version of the app.
