library(RSQLite)

#connect to db
con <- dbConnect(drv=RSQLite::SQLite(), dbname="project_data.sqlite")

#list all tables
tables <- dbListTables(con)

#exclude sqlite_sequence (contains table information)
tables <- tables[tables != "sqlite_sequence"]

TRACT_y <- vector("list", length=1)

#create a data.frame for each table
TRACT_y[[1]] <- dbGetQuery(conn=con, statement=paste("SELECT * FROM '", tables[[6]], "'", sep=""))
print(colnames(TRACT_y[[1]]))
gini= TRACT_y[[1]]$IncomeDisparityE
unemp= TRACT_y[[1]]$UnemploymentRateE
unins= TRACT_y[[1]]$P_UninsuredE
disa= TRACT_y[[1]]$P_WithADisabilityE
houseinc= TRACT_y[[1]]$MedianHouseholdIncomeE
housepr= TRACT_y[[1]]$MedianHomePriceE
vehav= TRACT_y[[1]]$P_NoVehicleAvailableE
nonw= TRACT_y[[1]]$P_NonWhiteE
rb= TRACT_y[[1]]$P_RentBurdenedE
sp= TRACT_y[[1]]$P_SingleParentHouseholdE
tc= TRACT_y[[1]]$total_clinicians
y_pred= TRACT_y[[1]]$y_Pred

model = glm(tc~gini + unemp + unins + disa + houseinc + housepr + vehav + nonw + rb + sp + y_pred, family="poisson")
print(summary(model))

#Testing overall regression
p_value_o = 1-pchisq((172022710-69815192),(80603-80592))
print(p_value_o)