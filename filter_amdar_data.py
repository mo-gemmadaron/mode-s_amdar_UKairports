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

    period = 'summer' # 'summer' or 'winter'

    phase = 'ascent' # 'ascent' (5) or 'descent' (6)

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

    #---------------------------------------------------------------------    
    # 03. Loop through airports/dates and export individual ascents/descents
    #---------------------------------------------------------------------

    for airport in airport_name_list: # hopefully we can skip this step if we are looking at a large area

    	for date in date_list:

    		print('Loading data for: {0} {1}'.format(airport, date))

    		data_amdar = import_files(file_path, 'AMDARS', airport, date)

    		# Filter the dataframe for aircraft number and flight phase

    		aircraft_list = data_amdar.RGSN_NMBR.unique()
    		#aircraft_list = ["b'EU0973  '", "b'EU3072  '", "b'EU0523  '"]

    		for aircraft in aircraft_list:

    			print('Processing aircraft no: {0}'.format(aircraft))

    			aircraft_df = filter_data(data_amdar, 'RGSN_NMBR', aircraft)
    			aircraft_df.sort_values(by = 'TIME')


    			if phase == 'ascent':
    				phase_id = 5
    			if phase == 'descent':
    				phase_id = 6
    			
    			select_phase = aircraft_df[aircraft_df.FLGT_PHAS == phase_id].copy()
    			select_phase.reset_index(inplace=True)
    			
			#Split dataframes where the same aircraft has multiple ascents/descents (in a day)

    			if select_phase.empty == True:
    				pass
    			
    			else:
    				select_phase['gap'] = select_phase['TIME'].diff() > pd.to_timedelta('5 minute') # look for gaps > 5 mins 
    				select_phase[select_phase.gap]
    				
    				split_frames = list(split_dataframe_by_column(select_phase, "gap"))

    				if len(split_frames) == 0: 
    					select_phase.drop(['gap'], axis=1, inplace=True)

    					if phase == 'ascent':
    						select_phase = select_phase.sort_values(by = 'ALTD')
    					if phase == 'descent':
     						select_phase = select_phase.sort_values(by = 'ALTD', ascending=False)

    					if len(select_phase) > 5: # only output profiles with at least 5 points
    						select_phase.to_csv(os.path.join(out_path, 'AMDAR_{0}_{1}_{2}_{3}_1.csv'.format(airport, aircraft, date, phase )), index=False)

    				else:
    					for i in (1,len(split_frames)):
    						out = pd.DataFrame(split_frames[i - 1])

    						if phase == 'ascent':
    							out = out.sort_values(by = 'ALTD')
    						if phase == 'descent':
     							out = out.sort_values(by = 'ALTD', ascending=False)

    						if len(out) > 5: # only output profiles with at least 5 points
    							out.drop(['gap'], axis=1, inplace=True)
    							out.to_csv(os.path.join(out_path, 'AMDAR_{0}_{1}_{2}_{3}_{4}.csv'.format(airport, aircraft, date, phase, i)), index=False) 
    				
 		
  			
if __name__ == '__main__':
    main()


