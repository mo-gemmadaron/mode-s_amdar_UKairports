#!/usr/bin/env python3.8
# -*- coding: iso-8859-1 -*-

'''
filter_amdar_data.py

Code for exporting individual aircraft ascents and descents from AMDAR data

To run the code:
   ./filter_amdar_data.py

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
# Function for importing AMDAR files
#-----------------------------------------------

def import_amdar_files(file_path, data_type, airport, date):

    filename = '{0}/{1}/{2}/{1}_{3}.txt'.format(file_path, data_type, airport, date) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    data['TIME'] = data['TIME'].astype(str) # convert time to string so '--' can be replaced

    data['TIME'] = data['TIME'].str.replace('--', '00') # replace null seconds with 00   

    data['TIME'] = pd.to_datetime(data['TIME'], format='%Y%m%d%H%M%S')

    data.set_index('TIME', inplace=True)

    return(data)


#-----------------------------------------------
# Function for importing airport information file
#-----------------------------------------------

def import_airport_info(file_path_info):

    filename = '{0}/airports_GBonly.csv'.format(file_path_info)
    print(filename) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    return(data)


#-----------------------------------------------
# Function for importing runway information file
#-----------------------------------------------

def import_runway_info(file_path_info):

    filename = '{0}/runways.csv'.format(file_path_info)
    print(filename) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    return(data)


#-----------------------------------------------
# Function for filtering AMDAR data
#-----------------------------------------------

def filter_data(df, column, condition):

    filter = df[column] == condition
    filter_df = pd.DataFrame(df.loc[filter])

    return(filter_df)


#-----------------------------------------------
# Function for splitting datafame where column is True
#-----------------------------------------------

def split_dataframe_by_column(df, column):

    previous_index = df.index[0]

    for split_point in df[df[column]].index:
        yield df[previous_index:split_point]
        previous_index = split_point

    # Yield remainder of dataset
    try:
        yield df[split_point:]
    except UnboundLocalError:
        pass # There is no split point => Ignore


#-----------------------------------------------
# Function for calculating the orientation of the AMDAR data between consecutive points
#-----------------------------------------------

def calculate_orientation(df, lat_col, lon_col):

    geodesic = pyproj.Geod(ellps='WGS84')

    df['LAT2'] = df[lat_col].shift(1)
    df['LON2'] = df[lon_col].shift(1)

    list = []
    for i, row in df.iterrows():
    	long1 = row[lon_col]
    	lat1 = row[lat_col]
    	long2 = row['LON2']
    	lat2 = row['LAT2']
    	fwd_azimuth,back_azimuth,distance = geodesic.inv(long1, lat1, long2, lat2)
    	if back_azimuth <0:
    		back_azimuth = back_azimuth + 360
    	list.append(back_azimuth)

    df['orientation'] = list
    df.drop(['LAT2'], axis=1, inplace=True)
    df.drop(['LON2'], axis=1, inplace=True)
    
    return(df)


#-----------------------------------------------
# Function for finding nearest airport 
#-----------------------------------------------

def find_nearest_airport(df, phase, airport_info_df, airport_lat_col, airport_lon_col):

    if phase == 'ascent': # choose first row
    	lat2 = df.loc[0,'LAT' ]
    	lon2 = df.loc[0,'LON' ]

    if phase == 'descent': # choose last row
    	print(len(df)-1)
    	lat2 = df.loc[len(df)-1,'LAT' ]
    	lon2 = df.loc[len(df)-1,'LON' ]

    geodesic = pyproj.Geod(ellps='WGS84')

    list = []
    		
    for i, row in airport_info_df.iterrows():
    	lon1 = row[airport_lon_col]
    	lat1 = row[airport_lat_col]

    	fwd_azimuth,back_azimuth,distance = geodesic.inv(lon1, lat1, lon2, lat2)
    	list.append(distance)
    		
    airport_info_df['distance'] = list
  
    airport_nearest = airport_info_df[airport_info_df.distance == airport_info_df.distance.min()]
    airport_name = airport_nearest['name']
    print('Nearest airport is: '+airport_name)

    #df['nearest airport'] = airport_name

    to_list = airport_nearest['ident'].tolist()
    airport_id = to_list[0]
    
    return(airport_id, df)

#-----------------------------------------------
# Function for finding runway orienation of nearest airport 
#-----------------------------------------------

def find_runway_orientation (df, runway_info_df, airport_id):

    '''
    find_runway = runway_info_df.loc[runway_info_df['airport_ident'] == airport_id]
    find_runway.reset_index(inplace=True)
    runway_orient_he = find_runway.loc[0, 'he_heading_degT'] # choose first if more than one
    #runway_orient_le = find_runway.loc[0, 'le_heading_degT'] # choose first if more than one
    df['runway_orientation'] = runway_orient_he
    df['difference'] = df['runway_orientation'] - df['orientation']
    '''

    find_runway = runway_info_df.loc[runway_info_df['airport_ident'] == airport_id]
    find_runway.reset_index(inplace=True)
    runway_orient_he = find_runway.loc[0, 'he_heading_degT'] # choose first if more than one (find better way to do this)

    if runway_orient_he >=0 and runway_orient_he <180:
    	runway_orient_le = runway_orient_he + 180
    else:
    	runway_orient_le = runway_orient_he - 180
    
    df['runway_orientation_he'] = runway_orient_he
    df['runway_orientation_le'] = runway_orient_le
    df['difference_he'] = df['orientation'] -df['runway_orientation_he']
    df['difference_le'] = df['orientation'] -df['runway_orientation_le'] 

    return(df)


def main():

    #---------------------------------------------------------------------
    # 01. Settings (consider adding to command line)
    #---------------------------------------------------------------------

    file_path = '/data/users/gdaron/MetDB/'
    file_path_info = '/data/users/gdaron/Mode-S_altitude/AMDAR_location_issue/Runway_orientation/AirportInfo'
    out_path = '/data/users/gdaron/Mode-S_altitude/AMDAR_location_issue/Runway_orientation/AMDAR_filter'

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    start_date = datetime.date(2022,11,22)
    end_date = datetime.date(2022,11,22)

    phase = 'ascent' # 'ascent' (5) or 'descent' (6)

    min_points_in_profile = 5

    time_gap = '5 minutes' # used to find gaps in timeseries and separate aircraft that have multiple ascents/descents in one day

    airport_name_list = ['Aberdeen']
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
    # 04. Loop through airports/dates and find individual ascents/descents
    #---------------------------------------------------------------------

    for airport in airport_name_list: 

    	for date in date_list:

    		print('Loading data for: {0} {1}'.format(airport, date))

    		data_amdar = import_amdar_files(file_path, 'AMDARS', airport, date)

    		# Filter the dataframe for aircraft number and flight phase

    		aircraft_list = data_amdar.RGSN_NMBR.unique()

    		for aircraft in aircraft_list:

    			print('Processing aircraft no: {0}'.format(aircraft))

    			aircraft_df = filter_data(data_amdar, 'RGSN_NMBR', aircraft)
    			aircraft_df.sort_values(by = 'TIME')


    			if phase == 'ascent':
    				phase_id = 5
    			if phase == 'descent':
    				phase_id = 6
    			
    			select_phase = aircraft_df[aircraft_df.FLGT_PHAS == phase_id].copy()
    			select_phase = select_phase[select_phase.ALTD < 1000] # Retain only data below 1000 m

    			select_phase.reset_index(inplace=True)
    			
			#Split dataframes where the same aircraft has multiple ascents/descents (in a day)

    			if select_phase.empty == True:
    				pass
    			
    			else:
    				select_phase['gap'] = select_phase['TIME'].diff() > pd.to_timedelta(time_gap) # look for gaps  
    				select_phase[select_phase.gap]
    				
    				split_frames = list(split_dataframe_by_column(select_phase, "gap"))

    				if len(split_frames) == 0: 
    					select_phase.drop(['gap'], axis=1, inplace=True)

    					if phase == 'ascent':
    						select_phase = select_phase.sort_values(by = 'ALTD')
    					if phase == 'descent':
     						select_phase = select_phase.sort_values(by = 'ALTD', ascending=False)

    					if len(select_phase) > min_points_in_profile: 
    						select_phase.reset_index(inplace=True)

    						calculate_orientation(select_phase, 'LAT', 'LON')

    						airport_id, select_phase = find_nearest_airport(select_phase, phase, airport_info, 'latitude_deg', 'longitude_deg')

    						find_runway_orientation (select_phase, runway_info, airport_id)
    						select_phase.drop(['index'], axis=1, inplace=True)
    						print(select_phase)

    						select_phase.to_csv(os.path.join(out_path, 'AMDAR_{0}_{1}_{2}_{3}_1.csv'.format(airport, aircraft, date, phase )), index=False, na_rep='NaN')
    						

    				else:
    					for i in (1,len(split_frames)):
    						out = pd.DataFrame(split_frames[i - 1])

    						if phase == 'ascent':
    							out = out.sort_values(by = 'ALTD')
    						if phase == 'descent':
     							out = out.sort_values(by = 'ALTD', ascending=False)

    						if len(out) > min_points_in_profile: 
    							out.drop(['gap'], axis=1, inplace=True)    					
    							out.reset_index(inplace=True)

    							calculate_orientation(out, 'LAT', 'LON')
   
    							airport_id, out = find_nearest_airport(out, phase, airport_info, 'latitude_deg', 'longitude_deg')

    							find_runway_orientation (out, runway_info, airport_id)
    							out.drop(['index'], axis=1, inplace=True)
    							print(out)    				

    							out.to_csv(os.path.join(out_path, 'AMDAR_{0}_{1}_{2}_{3}_{4}.csv'.format(airport, aircraft, date, phase, i)), index=False, na_rep='NaN')  		
  			
if __name__ == '__main__':
    main()


