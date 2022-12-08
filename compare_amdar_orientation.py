#!/usr/bin/env python3.8
# -*- coding: iso-8859-1 -*-

'''
compare_amdar_orientation.py

Code for calculating the orientation of AMDAR ascents/descents and compare with the nearest airport runway orientation

To run the code:
   ./compare_amdar_orientation.py

Author: gdaron
'''

import csv
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import dates
import datetime
from datetime import timedelta
import pyproj

#-----------------------------------------------
# Import aircraft ascent and descent profiles
#-----------------------------------------------

def import_files(file_path, airport, aircraft, date, phase):

    filename = '{0}/AMDAR_{1}_{2}_{3}_{4}_1.csv'.format(file_path, airport, aircraft, date, phase) # need to fix for number at end!!!!!
    print(filename) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    return(data)

#-----------------------------------------------
# Import airport information file
#-----------------------------------------------

def import_airport_info(file_path_info):

    filename = '{0}/airports.csv'.format(file_path_info)
    print(filename) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    return(data)

#-----------------------------------------------
# Import runway information file
#-----------------------------------------------

def import_runway_info(file_path_info):

    filename = '{0}/runways.csv'.format(file_path_info)
    print(filename) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    return(data)

#-----------------------------------------------
# Find nearest airport (This is very slow!)
#-----------------------------------------------

def find_nearest_airport(airport_info_df, airport_lat_col, airport_lon_col, lat2, lon2):

    geodesic = pyproj.Geod(ellps='WGS84')

    list = []
    		
    for i, row in airport_info_df.iterrows():
    	lon1 = row[airport_lon_col]
    	lat1 = row[airport_lat_col]

    	fwd_azimuth,back_azimuth,distance = geodesic.inv(lon1, lat1, lon2, lat2)
    	list.append(distance)
    		
    airport_info_df['distance'] = list
  
    airport_nearest = airport_info_df[airport_info_df.distance == airport_info_df.distance.min()]
    print('Nearest airport is: '+airport_nearest['name'])
    to_list = airport_nearest['ident'].tolist()
    airport_id = to_list[0]
    
    return(airport_id)


#-----------------------------------------------
# MAIN CODE
#-----------------------------------------------

def main():

    #---------------------------------------------------------------------
    # 01. Settings (consider adding to command line)
    #---------------------------------------------------------------------

    file_path = '/data/users/gdaron/Mode-S_altitude/AMDAR_filter'
    file_path_info = '/data/users/gdaron/Mode-S_altitude/AMDAR_location_issue/AirportInfo'
    out_path = '/data/users/gdaron/Mode-S_altitude/AMDAR_filter/out'

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    start_date = datetime.date(2022,11,22)
    end_date = datetime.date(2022,11,22)

    phase = 'ascent' # 'ascent' (5) or 'descent' (6)

    airport_name_list = ['AREA_test'] 

    aircraft_list = ["b'EU0149  '", "b'EU0454  '"]
    '''
    airport_name_list = ['Heathrow', \
                         'Gatwick', \
                         'Manchester', \
                         'Stansted', \
                         'Edinburgh', \
                         'Birmingham', \
                         'Bristol', \
                         'Glasgow', \
                         'Aberdeen', \
                         'EastMidlands', \
                         'LondonCity', \
                         'BelfastInt', \
                         'Newcastle', \
                         'LeedsBradford', \
                         'Liverpool',\
                         'Cardiff']
    '''

    #---------------------------------------------------------------------    
    # 02. Create date list
    #---------------------------------------------------------------------

    date_list = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    date_list = [date_obj.strftime('%Y%m%d') for date_obj in date_list]

    #---------------------------------------------------------------------    
    # 03. Import airport and runway information
    #---------------------------------------------------------------------

    airport_info = import_airport_info(file_path_info)
    runway_info = import_runway_info(file_path_info)

    #---------------------------------------------------------------------    
    # 04. Loop through airports/dates and compare orientations with runway orientation of nearest airport
    #---------------------------------------------------------------------

    for airport in airport_name_list: # hopefully we can skip this step if we are looking at a large area

    	for date in date_list:

    		for aircraft in aircraft_list:

    			print('Loading data for: {0} {1} {2}'.format(airport, date, aircraft))

    			data_amdar = import_files(file_path, airport, aircraft, date, phase)

    			if phase == 'ascent': # choose first row
    				lat2 = data_amdar.loc[0,'LAT' ]
    				lon2 = data_amdar.loc[0,'LON' ]

    			if phase == 'descent': # choose last row
    				lat2 = data_amdar.loc[len(data_amdar)-1,'LAT' ]
    				lon2 = data_amdar.loc[len(data_amdar)-1,'LON' ]

    			airport_id = find_nearest_airport(airport_info, 'latitude_deg', 'longitude_deg', lat2, lon2)

    			#search for runway orientation of airport id
    			out = runway_info.loc[runway_info['airport_ident'] == airport_id]
    			out.reset_index(inplace=True)
    			runway_orient = out.loc[0, 'le_heading_degT'] # choose first if more than one
    			data_amdar['runway_orientation'] = runway_orient
    			data_amdar['difference'] = data_amdar['runway_orientation'] - data_amdar['orientation']
    			print(data_amdar)


			
if __name__ == '__main__':
    main()


