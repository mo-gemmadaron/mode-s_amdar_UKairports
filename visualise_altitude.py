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


def main():

    #---------------------------------------------------------------------
    # 01. Settings
    #---------------------------------------------------------------------

    file_path = '/data/users/gdaron/MetDB/'
    out_path = '/data/users/gdaron/Mode-S_altitude/Mode-S_vs_AMDAR'

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    period = 'summer' # summer or winter

    if period == 'summer':
    	start_date = datetime.date(2021,7,10)
    	end_date = datetime.date(2021,8,10)

    if period == 'winter':
    	start_date = datetime.date(2022,1,1)
    	end_date = datetime.date(2022,1,31)

    date_list = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    date_list = [date_obj.strftime('%Y%m%d') for date_obj in date_list]

    #airport_name_list = ['Bristol', 'Heathrow']
    
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
    

    # Set y axis ranges
    y_max = 3000 # useful if all plots have the same axis ranges
    y_min = -250 

    #---------------------------------------------------------------------    
    # 02. Loop through airports/dates and plot altitude
    #---------------------------------------------------------------------

    diff_df = pd.DataFrame()

    for airport in airport_name_list:

    	concat_amdar = pd.DataFrame()
    	concat_modes = pd.DataFrame()
    	concat_amdar_day_min = pd.DataFrame()
    	concat_modes_day_min = pd.DataFrame()

    	for date in date_list:

    		print('Loading data for: {0} {1}'.format(airport, date))

    		data_amdar = import_files(file_path, 'AMDARS', airport, date)
    		data_modes = import_files(file_path, 'MODE-S', airport, date)

    		# Find row containing daily min
    		data_amdar_day_min = data_amdar[data_amdar.ALTD==data_amdar.ALTD.min()]
    		data_modes_day_min = data_modes[data_modes.PESR_ALTD==data_modes.PESR_ALTD.min()]

    		concat_amdar = pd.concat([concat_amdar, data_amdar])
    		concat_modes = pd.concat([concat_modes, data_modes])

    		concat_amdar_day_min = pd.concat([concat_amdar_day_min, data_amdar_day_min])
    		concat_modes_day_min = pd.concat([concat_modes_day_min, data_modes_day_min])

    	# Create dataframe of daily minimum AMDAR and Mode-S altitudes 
    	concat_amdar_day_min.reset_index(inplace=True)         
    	concat_amdar_day_min['TIME'] = concat_amdar_day_min['TIME'].dt.strftime('%Y%m%d')    
    	concat_amdar_day_min = concat_amdar_day_min.drop_duplicates(['TIME'], keep='first')    	

    	concat_modes_day_min.reset_index(inplace=True)         
    	concat_modes_day_min['TIME'] = concat_modes_day_min['TIME'].dt.strftime('%Y%m%d')    
    	concat_modes_day_min = concat_modes_day_min.drop_duplicates(['TIME'], keep='first')

    	concat_amdar_day_min['TIME'] = pd.to_datetime(concat_amdar_day_min['TIME'], format='%Y%m%d')
    	concat_modes_day_min['TIME'] = pd.to_datetime(concat_modes_day_min['TIME'], format='%Y%m%d')

    	concat_amdar_day_min.set_index('TIME', inplace=True)
    	concat_modes_day_min.set_index('TIME', inplace=True)

    	diff = concat_modes_day_min['PESR_ALTD'] - concat_amdar_day_min['ALTD']
    	mean_diff = diff.mean(axis=0)
    	mean_min_amdar_altd = concat_amdar_day_min['ALTD'].mean(axis=0)
    	mean_min_modes_altd = concat_modes_day_min['PESR_ALTD'].mean(axis=0)
    	series = pd.Series([airport, mean_diff, mean_min_amdar_altd, mean_min_modes_altd])
    	diff_df = pd.concat([diff_df, series], axis=1)
        	
    	# Plot data (multiple days)
    	'''
    	#start_date_reformat = start_date.strftime('%d/%m/%Y')
    	#end_date_reformat = end_date.strftime('%d/%m/%Y')

    	fig2, ax2 = plt.subplots(figsize=(6,6))
    	plt.plot(concat_modes['PESR_ALTD'], marker='.', markersize=2, color ='#1f77b4', linestyle='None', label='Mode-S')
    	plt.plot(concat_amdar['ALTD'], marker='.', markersize=2, color='#d62728', linestyle='None', label='AMDAR')
    	#plt.plot(concat_modes_day['PESR_ALTD'], marker='.', color ='#1f77b4', linestyle='--', linewidth=2, label='Mode-S pressure altitude (daily min)')
    	#plt.plot(concat_modes_day['GNSS_ALTD'], marker='.', color ='black', linestyle='--', linewidth=2, label='Mode-S GNSS altitude (daily min)')
    	#plt.plot(concat_amdar_day['ALTD'], marker='.', color='#d62728', linestyle='-', linewidth=2, label='AMDAR pressure altitude (daily min)')

    	#ax2.set_title('{0} airport '.format(airport)+str(start_date_reformat)+' to '+str(end_date_reformat))
    	ax2.set_title('{0} airport - {1}'.format(airport, period))

    	ax2.set_xlabel('Date')
    	ax2.set_xlim([start_date, end_date])
    	ax2.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
    	#ax2.xaxis.set_major_locator(dates.DayLocator(interval=7))
    	ax2.set_xticks(np.arange(start_date, end_date, 7))

    	ax2.set_ylabel('Altitude / m')
    	ax2.set_ylim([y_min, y_max])

    	plt.legend(loc='upper right', prop={'size':12}, facecolor='white')
    	ax2.axhline(y=0, xmin=0, xmax=1, linewidth =1, linestyle = '--', color='black')
    	#ax2.annotate( 'Mean daily min (Mode-S GNSS): ' + str(round(modes_GNSS_mean,0)) , xy = (10,10), xycoords = 'axes points')
    	plt.tight_layout()
    	plt.savefig(os.path.join(out_path, "{0}_{1}.jpg".format(airport, period)))
    	#plt.show() 
    	plt.close(fig2)
    	'''

    	# Plot daily minimun altitude data 
  
    	fig3, ax3 = plt.subplots(figsize=(6,6))
    	plt.plot(concat_modes_day_min['PESR_ALTD'], marker='.', color ='#1f77b4', linestyle='-', label='Mode-S pressure altitude (daily min)')
    	plt.plot(concat_amdar_day_min['ALTD'], marker='.', color='#d62728', linestyle='-', label='AMDAR pressure altitude (daily min)')

    	#ax3.set_title('{0} airport (daily min altd) '.format(airport)+str(start_date_reformat)+' to '+str(end_date_reformat))
    	ax3.set_title('{0} airport - {1}'.format(airport, period))

    	ax3.set_xlabel('Date')
    	ax3.set_xlim([start_date, end_date])
    	ax3.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
    	ax3.set_xticks(np.arange(start_date, end_date, 7))

    	ax3.set_ylabel('Altitude / m')
    	ax3.set_ylim([y_min, y_max])

    	plt.legend(loc='upper right', prop={'size':12}, facecolor='white')
    	ax3.axhline(y=0, xmin=0, xmax=1, linewidth =1, linestyle = '--', color='black')
    	plt.tight_layout()

    	out_path_day_min = out_path+'/daily_min'

    	if not os.path.exists(out_path_day_min):
        	os.makedirs(out_path_day_min)

    	plt.savefig(os.path.join(out_path_day_min, '{0}_day_min_altd_{1}.jpg'.format(airport, period)))
    	#plt.show() 
    	plt.close(fig3)


    diff_df = diff_df.transpose()
    diff_df.columns = ['Airport', 'Mode-S (mean daily min) - AMDAR (mean daily min)', 'AMDAR (mean daily min)', 'Mode-S (mean daily min)']
    diff_df.to_csv(os.path.join(out_path_day_min, 'Mode-S-AMDAR_daily_mins_{0}.csv'.format(period)), index=False)


if __name__ == '__main__':
    main()


