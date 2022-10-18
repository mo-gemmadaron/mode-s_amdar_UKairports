# mode-s_amdar_UKairports

add_missing_amdar_headers.py
add_missing_modes_headers.py
When data is extracted from MetDB, a missing quarter may result in a missing header. These scripts check for missing headers and add headers if necessary.

visualise_altitude.py
Loads and plots altitude data for Mode-S and AMDAR observations. Set for 2 periods (Jan 2022 and Jul/Aug 2021).

JUPYTER NOTEBOOKS - for use in ArcGIS

Note - this methodology works for a small set of dates or airports, but step 2 takes a very long time if looking at a month of data for lots of airports. I have therefore reverted to using a python script on the VDI.

1. Create_runway_polygons.ipynb - uses information about the location of the aiport and orientation of the runway, to create a polygon for subsetting the data. NB - given the AMDAR location issues, these have not been used.

2. Load_data_into_ArcGIS_Pro.ipynb - loads inividual days of data for both AMDAR and Mode-S. Includes function for updating the symbology for viewing in the map layout.

3.  Altitude_analysis.ipynb - converts the loaded data into dataframes and plots altitudes.
