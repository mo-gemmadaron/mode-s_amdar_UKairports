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

    filename = '{0}/AMDAR_{1}_{2}_{3}_{4}_1.csv'.format(file_path, airport, aircraft, date, phase)
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

    type_dict = {'latitude_deg': 'float32', 'longitude_deg': 'float32'}
    data = pd.read_csv(filename, dtype=type_dict)

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

    period = 'summer' # 'summer' or 'winter'

    phase = 'ascent' # 'ascent' (5) or 'descent' (6)

    airport_name_list = ['Heathrow_test'] 

    aircraft = "b'EU0322  '"
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

    if period == 'summer':
    	start_date = datetime.date(2022,11,22)
    	end_date = datetime.date(2022,11,22)
    	#start_date = datetime.date(2021,7,10)
    	#end_date = datetime.date(2021,7,10)

    if period == 'winter':
    	start_date = datetime.date(2022,1,1)
    	end_date = datetime.date(2022,1,31)

    date_list = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    date_list = [date_obj.strftime('%Y%m%d') for date_obj in date_list]
    print(date_list)

    #---------------------------------------------------------------------    
    # 03. Loop through airports/dates and export individual ascents/descents
    #---------------------------------------------------------------------

    airport_info = import_airport_info(file_path_info)
    print(airport_info)

    runway_info = import_runway_info(file_path_info)
    print(runway_info)


    for airport in airport_name_list: # hopefully we can skip this step if we are looking at a large area

    	for date in date_list:

    		print('Loading data for: {0} {1}'.format(airport, date))

    		data_amdar = import_files(file_path, airport, aircraft, date, phase)
    		print(data_amdar)

    		if phase == 'ascent':
    			lat2 = data_amdar.loc[0,'LAT' ]
    			long2 = data_amdar.loc[0,'LON' ]
    			print(lat2)
    			print(long2)

    		if phase == 'descent':
    			lat2 = data_amdar.loc[len(data_amdar)-1,'LAT' ]
    			long2 = data_amdar.loc[len(data_amdar)-1,'LON' ]
    			print(lat2)
    			print(long2)

    		#search for ident of nearest airport

    		geodesic = pyproj.Geod(ellps='WGS84')

    		list = []
    		for i, row in airport_info.iterrows():
    			long1 = row['longitude_deg']
    			lat1 = row['latitude_deg']

    			fwd_azimuth,back_azimuth,distance = geodesic.inv(long1, lat1, long2, lat2)
    			list.append(distance)
    		
    		airport_info['distance'] = list
  
    		airport_nearest = airport_info[airport_info.distance == airport_info.distance.min()]
    		#airport_id.reset_index(inplace=True)
    		airport_id = airport_nearest['ident']
    		test = airport_id.tolist()
    		test2 = test[0]
    		print(test2)

    		#search for runway orientation of airport id
    		#print(runway_info.loc[runway_info['airport_ident'] == 'EGLL'])
    		out = runway_info.loc[runway_info['airport_ident'] == test2]
    		out.reset_index(inplace=True)
    		print(out)
    		test3 = out.loc[0, 'he_heading_degT']
    		print(test3)

    		data_amdar['runway_orientation'] = test3
    		print(data_amdar)

    		data_amdar['difference'] = data_amdar['runway_orientation'] - data_amdar['orientation']
    		print(data_amdar)

			
if __name__ == '__main__':
    main()


