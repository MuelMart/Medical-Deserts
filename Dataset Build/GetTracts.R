packages <- c('tidyverse', 'tidycensus', 'RSQLite', 'DBI', 'tigris', 'sf')

#Load in packages
for(p in packages){
  if (!(p %in% installed.packages())){
    install.packages(p)
  }
  
  library(p, character.only = TRUE)
}

acs_vars <- c(
  'IncomeDisparity' = 'B19083_001',
  
  'UnemploymentRate' = 'S2301_C04_001',
  
  'P_Uninsured' = 'S2701_C05_001',
  
  'P_WithADisability' = 'S1810_C03_001',
  
  'MedianHouseholdIncome' = 'S1901_C01_012',
  
  'P_SingleMaleHHChildren' = 'DP02_0007P', #Add this to P_SingleFemaleHHChildren
  'P_SingleFemaleHHChildren' = 'DP02_0011P', #Add this to P_SingleMaleHHChildren
  
  'MedianHomePrice' = 'DP04_0089',
  'P_30-34Rent' = 'DP04_0141P', #Add this P_35+Rent
  'P_35+Rent' = 'DP04_0142P', #Add this to P_30-34Rent
  'P_NoVehicleAvailable' = 'DP04_0058P',
  
  'P_White' = 'DP05_0037P' #Subtract from 100 to get Percent Nonwhite
)

############
#Function to pull tracts given ACS variables from above.
############
get_tracts <- function(key, state = NA, year = 2021, vars = acs_vars, geometry = TRUE){
  
  #Activate API key
  census_api_key(key)
  
  #Get tracts if states are undefined
  if(is.na(state)){
    
    #Get FIPS for every state (not including territories)
    state_fips <- fips_codes %>%
      group_by(state, state_code) %>%
      filter(state_code < 57) %>%
      summarize()
    
    #For each state, query tracts and bind together
    tracts <- data_frame()
    for(state in state_fips$state){
      tract_state <- get_acs('tract', variables = vars, year = year, state = state, output = 'wide', geometry = geometry) %>%
        mutate('state' = state)
      
      #Bind
      tracts <- tracts %>%
        rbind(tract_state)
    }
    

  }
  
  else{
    tracts <- get_acs('tract', variables = vars, year = year, state = state, output = 'wide', geometry = geometry)
  }
  
  #Remove margins of error
  tracts_clean <- tracts %>%
    select(-ends_with('M'))
  
  return(tracts_clean)
}

############
#Function to process and clean data
############
process_tracts <- function(data){
  
  tracts_clean <- data %>%
    
    #Get percent nonwhite by subtracting 100 from P_White
    mutate('P_NonWhiteE' = 100 - `P_WhiteE`, .keep = 'unused') %>%
    
    #Calculate percent rent burdened
    mutate('P_RentBurdenedE' = `P_30-34RentE` + `P_35+RentE`, .keep = 'unused') %>%
    
    #Calculate percent single family householders
    mutate('P_SingleParentHouseholdE' = `P_SingleMaleHHChildrenE` + `P_SingleFemaleHHChildrenE`, .keep = 'unused')
  
  return(tracts_clean)
  
}

############
#Function to read data to SQLITE DB
############
write_tracts_to_sqlite <- function(data, dbPath){
  
  #Remove geometries from acs data
  geometries <- data %>%
    select(c(GEOID, geometry))
  no_geometries <- data %>%
   st_drop_geometry()
  
  #Connect to db
  conn = dbConnect(RSQLite::SQLite(), dbPath)
  
  #Write table to database
  dbWriteTable(conn, 'TRACTS', no_geometries, overwrite = TRUE)
  st_write(geometries, dsn = conn, layer = 'TRACT_GEOMETRIES')
  
  dbDisconnect(conn)
}

###
#QUERY DATA AND UPDATE DB
###
tracts <- get_tracts(Sys.getenv('census_api')) %>%
  process_tracts()

write_tracts_to_sqlite(tracts, '../project_data.sqlite')


