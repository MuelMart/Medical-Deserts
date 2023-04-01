# A Spatial and Computational Analysis of Medical Deserts
This repository serves as the codebase for our CSE6242 final project.
>The objective of our research is to utilize an analytical approach to identify and understand the characteristics of medical deserts. We plan to achieve this task by leveraging American Community Survey 5-year Estimate data alongside Centers for Medicare & Medicaid Services data. With this data, we intend to calculate the number of family practice doctor’s offices within a 25 km radius of each tract centroid in the country. A clustering model will be applied to the data to identify discrete groups that exhibit similar demographic characteristics, socioeconomic characteristics (e.g. tract poverty rate, median household income, etc.), as well as healthcare facility access. Additionally, the researchers will employ a regularized regression model to identify which socioeconomic / demographic characteristics are most important in determining the number of doctors within a 25 km radius of a tract. The final product will come in the form of an interactive map which displays which tracts are most vulnerable with respect to healthcare access alongside additional information regarding the demographic profile of said tracts. The hope is that this project can provide a new perspective to understanding the mechanisms through which inequity can perpetuate the hinderance of medical access.

### Table of Contents
[Data Dictionary](###-data-dictionary)


### Data Dictionary
The dataset is housed in a SQLite database, which contains the following tables:

- TRACTS
- DOCTORS_RAW
- DOCTORS
- DOCTORS_LOCATIONS
