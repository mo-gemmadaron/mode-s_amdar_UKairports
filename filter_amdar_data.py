#!/usr/bin/env python3.8
# -*- coding: iso-8859-1 -*-

'''
visualise_altitude.py

Code for plotting the altitude for Mode-S and AMDAR data near UK airports

To run the code:
   ./visualise_altitude.py

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



def import_files(file_path, data_type, airport, date):

    filename = '{0}/{1}/{2}/{1}_{3}.txt'.format(file_path, data_type, airport, date) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    data['TIME'] = data['TIME'].astype(str) # convert time to string so '--' can be replaced

    data['TIME'] = data['TIME'].str.replace('--', '00') # replace null seconds with 00   

    data['TIME'] = pd.to_datetime(data['TIME'], format='%Y%m%d%H%M%S')

    data.set_index('TIME', inplace=True)

    return(data)


def filter_data(df, column, condition):

    filter = df[column] == condition
    filter_df = pd.DataFrame(df.loc[filter])

    return(filter_df)


def split_dataframe_by_column(df, column):

    """Split a DataFrame where a column is True. Yields a number of dataframes"""

    previous_index = df.index[0]

    for split_point in df[df[column]].index:
        yield df[previous_index:split_point]
        previous_index = split_point

    # Yield remainder of dataset
    try:
        yield df[split_point:]
    except UnboundLocalError:
        pass # There is no split point => Ignore


def main():

    #---------------------------------------------------------------------
    # 01. Settings
    #---------------------------------------------------------------------

    file_path = '/data/users/gdaron/MetDB/'
    out_path = '/data/users/gdaron/Mode-S_altitude/AMDAR_filter'

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    period = 'summer' # summer or winter

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

    airport_name_list = ['Heathrow_test']
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
    # 02. Loop through airports/dates, filter and add flags
    #---------------------------------------------------------------------

    for airport in airport_name_list:

    	concat_amdar = pd.DataFrame()

    	for date in date_list:

    		print('Loading data for: {0} {1}'.format(airport, date))

    		data_amdar = import_files(file_path, 'AMDARS', airport, date)

    		concat_amdar = pd.concat([concat_amdar, data_amdar])

    	# Filter the dataframe for aircraft number and flight phase

    	aircraft_list = concat_amdar.RGSN_NMBR.unique()
    	#aircraft_list = ["b'EU6614  '", "b'EU0627  '"]

    	for aircraft in aircraft_list:

    		aircraft_df = filter_data(concat_amdar, 'RGSN_NMBR', aircraft)

    		#aircraft_filter = concat_amdar['RGSN_NMBR'] == aircraft
    		#aircraft_df = pd.DataFrame(concat_amdar.loc[aircraft_filter])
    		aircraft_df.sort_values(by = 'TIME')

    		phase_list = aircraft_df.FLGT_PHAS.unique()

    		for phase in phase_list:
    			#phase_filter = aircraft_df['FLGT_PHAS'] == phase
    			#phase_df = pd.DataFrame(aircraft_df.loc[phase_filter])
    			phase_df = filter_data(aircraft_df, 'FLGT_PHAS', phase)
    			phase_df.reset_index(inplace=True)

    			#Split dataframes where the same aircraft has multiple ascents/descents (in a day)
    			
    			select_phase = phase_df[phase_df.FLGT_PHAS == 5] # select ascent 
    			#print(select_phase)

    			if select_phase.empty == True:
    				pass
    			else:

    				select_phase['gap'] = select_phase['TIME'].sort_values().diff() > pd.to_timedelta('1 hour')
    				select_phase[select_phase.gap]
    				#print(select_phase)

    				split_frames = list(split_dataframe_by_column(select_phase, "gap"))
    				#print(len(split_frames))

    				if len(split_frames) == 0:
    					print(select_phase)

    				else:
    					for i in (1,len(split_frames)):
    						out = pd.DataFrame(split_frames[i - 1])
    						print(out)
    		

if __name__ == '__main__':
    main()

