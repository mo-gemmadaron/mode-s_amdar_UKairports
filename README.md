# mode-s_amdar_UKairports

## Python code
* **add_missing_amdar_headers.py / add_missing_modes_headers.py**

When data is extracted from MetDB, a missing quarter may result in a missing header. These scripts check for missing headers and add headers if necessary.


* **visualise_altitude.py**

Loads and plots altitude data for Mode-S and AMDAR observations. Set for 2 periods (Jan 2022 and Jul/Aug 2021). Also extracts the daily minimums for comparison.


* **compare_modes_model.py**

Loads the locations of the daily minimums in British Grid (output from Altitude_analysis.ipynb below)  and the netcdf files of modelled "minimum detectable altitude" provided by Sharon Jewell. The code extracts the netcdf data at the given locations (picks nearest cell to the west/south). Outputs and plots data for report.



## Jupyter Notebooks - for use in ArcGIS

Note - this methodology works for a small set of dates or airports, but step 2 takes a very long time if looking at a month of data for lots of airports. I have therefore reverted to using a python script on the VDI to compare the altitude data.

* **1.Create_runway_polygons.ipynb** 

Uses information about the location of the aiport and orientation of the runway, to create a polygon for subsetting the data. NB - given the AMDAR location issues, these have not been used.


* **2.Load_data_into_ArcGIS_Pro.ipynb** 

Loads inividual days of data for both AMDAR and Mode-S. Includes function for updating the symbology for viewing in the map layout.


* **3.Altitude_analysis.ipynb** 

Converts the loaded data into dataframes and plots altitudes. For the report, **visualise_altitude.py** has been used for this step.


* **4.Convert_daily_min_lat_lon**

Loads the data as dataframes (does not plot) and extracts the locations of the daily minimum values for the Mode-S data. This is then converted to British Grid and exported (for use in **compare_modes_model.py**)
