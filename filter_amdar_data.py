#!/usr/bin/env python3.8
# -*- coding: iso-8859-1 -*-

'''
filter_amdar_data.py

Code for exporting individual aircraft Ascents and Descents from AMDAR data

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
from matplotlib.ticker import PercentFormatter


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

    filename = '{0}/airports_GBonly_study.csv'.format(file_path_info)
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
    	
    	if lat1 == lat2 and long1 == long2:
    		back_azimuth = float('NaN') # don't calculate orientation if points are at the same location
    	else:
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

    if phase == 'Ascent': # choose first row
    	lat2 = df.loc[0,'LAT' ]
    	lon2 = df.loc[0,'LON' ]

    if phase == 'Descent': # choose last row
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
    to_list = airport_nearest['name'].tolist()
    airport_name = to_list[0]

    print('Nearest airport is: '+airport_name)

    df['nearest airport'] = airport_name

    to_list = airport_nearest['ident'].tolist()
    airport_id = to_list[0]
    
    return(airport_id, df)

#-----------------------------------------------
# Function for finding runway orienation of nearest airport 
#-----------------------------------------------

def find_runway_orientation (df, runway_info_df, airport_id):

    find_runway = runway_info_df.loc[runway_info_df['airport_ident'] == airport_id]
    find_runway.reset_index(inplace=True)

    find_runway_longest = find_runway[find_runway.length_ft == find_runway.length_ft.max()] # choose longest runway if more than one
    to_list = find_runway_longest['he_heading_degT'].tolist()
    runway_orient_he = to_list[0]

    if runway_orient_he >=0 and runway_orient_he <180:
    	runway_orient_le = runway_orient_he + 180
    else:
    	runway_orient_le = runway_orient_he - 180
    
    df['runway_orientation_he'] = runway_orient_he
    df['runway_orientation_le'] = runway_orient_le

    df['difference_he'] = (df['orientation'] - df['runway_orientation_he'] + 180 + 360) % 360 - 180 
    df['difference_le'] = (df['orientation'] - df['runway_orientation_le'] + 180 + 360) % 360 - 180
    return(df)

#-----------------------------------------------
# Function for finding individual Ascents/Descents and comparing orientation with the runway orientation 
#-----------------------------------------------

def compare_orientation(df, phase, min_points_in_profile, airport_info_df, runway_info_df, summary_df):


    if 'gap' in df.columns:
    	df.drop(['gap'], axis=1, inplace=True)

    if phase == 'Ascent':
    	df = df.sort_values(by = 'ALTD')
    if phase == 'Descent':
    	df = df.sort_values(by = 'ALTD', ascending=False)

    df.reset_index(inplace=True)

    calculate_orientation(df, 'LAT', 'LON')

    airport_id, df = find_nearest_airport(df, phase, airport_info_df, 'latitude_deg', 'longitude_deg')

    find_runway_orientation (df, runway_info_df, airport_id)
    df.drop(['index'], axis=1, inplace=True)

    if phase == 'Ascent':
    	test = pd.DataFrame(df.iloc[1,:])
    	test = test.transpose()
    if phase == 'Descent':
    	test = pd.DataFrame(df.iloc[len(df)-1,:])
    	test = test.transpose()

    summary_df = pd.concat([summary_df, test])
    
    return(df, summary_df)					


def main():

    #---------------------------------------------------------------------
    # 01. Settings (consider adding to command line)
    #---------------------------------------------------------------------

    file_path = '/data/users/gdaron/MetDB/'
    file_path_info = '/data/users/gdaron/Mode-S_altitude/AMDAR_location_issue/Runway_orientation/AirportInfo'
    out_path = '/data/users/gdaron/Mode-S_altitude/AMDAR_location_issue/Runway_orientation/AMDAR_filter'

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    period = 'Jul18' # 'Jul13', 'Nov22', 'Jul20' or 'Jul18' (these are the periods extracted from MetDb)

    phase = 'Descent' # 'Ascent' (5) or 'Descent' (6)

    min_points_in_profile = 2

    time_gap = '5 minutes' # used to find gaps in timeseries and separate aircraft that have multiple Ascents/Descents in one day

    #airport_name_list = ['Gatwick']
    
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
    

    #---------------------------------------------------------------------    
    # 02. Create date list
    #---------------------------------------------------------------------

    if period == 'Nov22':
    	start_date = datetime.date(2022,11,22)
    	end_date = datetime.date(2022,11,28)
    if period == 'Jul20':
    	start_date = datetime.date(2020,7,22)
    	end_date = datetime.date(2020,7,28)
    if period == 'Jul18':
    	start_date = datetime.date(2018,7,22)
    	end_date = datetime.date(2018,7,28)
    if period == 'Jul13':
    	start_date = datetime.date(2013,7,22)
    	end_date = datetime.date(2013,7,28)

    date_list = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    date_list = [date_obj.strftime('%Y%m%d') for date_obj in date_list]

    #---------------------------------------------------------------------    
    # 03. Import airport and runway information
    #---------------------------------------------------------------------

    airport_info = import_airport_info(file_path_info)
    runway_info = import_runway_info(file_path_info)

    #---------------------------------------------------------------------    
    # 04. Loop through airports/dates and find individual Ascents/Descents
    #---------------------------------------------------------------------

    for_hist = pd.DataFrame()

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


    			if phase == 'Ascent':
    				phase_id = 5
    			if phase == 'Descent':
    				phase_id = 6
    			
    			select_phase = aircraft_df[aircraft_df.FLGT_PHAS == phase_id].copy()
    			select_phase = select_phase[select_phase.ALTD < 1000] # Retain only data below 1000 m

    			select_phase.reset_index(inplace=True)
    			
			#Split dataframes where the same aircraft has multiple Ascents/Descents (in a day)

    			if select_phase.empty == True:
    				print("There are no data for this aircraft and phase on this date")
    				pass
    			
    			else:
    				select_phase['gap'] = select_phase['TIME'].diff() > pd.to_timedelta(time_gap) # look for gaps  
    				select_phase[select_phase.gap]
    				
    				split_frames = list(split_dataframe_by_column(select_phase, "gap"))

    				if len(split_frames) == 0:
    					if len(select_phase) > min_points_in_profile:
    						select_phase, for_hist = compare_orientation(select_phase, phase, min_points_in_profile, airport_info, runway_info, for_hist)
    						#select_phase.to_csv(os.path.join(out_path, 'AMDAR_{0}_{1}_{2}_{3}_1.csv'.format(airport, aircraft, date, phase )), \
                                                                    #index=False, na_rep='NaN')

    				else:
    					for i in (1,len(split_frames)):
    						split_df = pd.DataFrame(split_frames[i - 1])
    						if len(split_df) > min_points_in_profile:
    							split_df, for_hist = compare_orientation(split_df, phase, min_points_in_profile, airport_info, runway_info, for_hist)
    							#split_df.to_csv(os.path.join(out_path, 'AMDAR_{0}_{1}_{2}_{3}_1.csv'.format(airport, aircraft, date, phase )), \
                                                                        #index=False, na_rep='NaN')


    #summarise data for plotting
    for_hist['abs_difference_min'] = abs(for_hist[['difference_he','difference_le']]).min(axis=1)
    for_hist = for_hist.sort_values(by = 'abs_difference_min', ascending=True)
    for_hist.to_csv(os.path.join(out_path, 'Summary_{0}_{1}.csv'.format(phase, period)), index=False, na_rep='NaN')
    #print(for_hist)

    fig1, ax1 = plt.subplots(figsize=(4,4))
    bins = [0,10,20,30,40,50,60,70,80,90]
    plt.hist(for_hist['abs_difference_min'], weights=np.ones(len(for_hist['abs_difference_min'])) / len(for_hist['abs_difference_min']), bins=bins)
    num_points = len(for_hist.dropna())
    ax1.annotate( 'No. of profiles: ' + str(num_points) , xy = (125,200), xycoords = 'axes points')
    ax1.set_title('{0} {1}'.format(phase, period))
    ax1.set_xlabel('Angle (deg)')
    ax1.set_xlim([0, 90])
    ax1.set_xticks(np.arange(0, 90, 10))
    #ax1.set_ylabel('%')
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    ax1.set_ylim([0, 1])
    plt.tight_layout()
    plt.savefig(os.path.join(out_path, 'Summary_hist_{0}_{1}.jpg'.format(phase, period)))
    plt.close(fig1)
    #plt.show()  		
  			
if __name__ == '__main__':
    main()


