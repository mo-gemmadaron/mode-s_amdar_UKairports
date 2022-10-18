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
    # 01. Set user inputs
    #---------------------------------------------------------------------

    file_path = '/data/users/gdaron/MetDB/'
    out_path = '/data/users/gdaron/Mode-S_altitude/'

    start_date = datetime.date(2021,7,10)
    end_date = datetime.date(2021,8,10)

    date_list = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    date_list = [date_obj.strftime('%Y%m%d') for date_obj in date_list]

    #airport_name_list = ['Bristol']
    
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
    # 02. Loop through airports/dates and plot altitude
    #--------------------------------------------------------------------- 

    for airport in airport_name_list:

    	concat_amdar = pd.DataFrame()
    	concat_modes = pd.DataFrame()

    	for date in date_list:

    		print('Loading data for: {0} {1}'.format(airport, date))

    		data_amdar = import_files(file_path, 'AMDARS', airport, date)
    		data_modes = import_files(file_path, 'MODE-S', airport, date)

    		concat_amdar = pd.concat([concat_amdar, data_amdar])
    		concat_modes = pd.concat([concat_modes, data_modes])

    		# Resample data and get hourly min altitude
    		concat_amdar_hour = concat_amdar.resample('H').min()
    		concat_modes_hour = concat_modes.resample('H').min()

    		# Resample data and get daily min altitude
    		concat_amdar_day = concat_amdar.resample('D').min()
    		concat_modes_day = concat_modes.resample('D').min()

    		# Calculate mean daily min 
    		modes_GNSS_mean = concat_modes_day['GNSS_ALTD'].mean()
    		modes_pressure_mean = concat_modes_day['PESR_ALTD'].mean()
    		amdar_pressure_mean = concat_amdar_day['ALTD'].mean()

    		# Set y axis ranges
    		y_max = 3000 # useful if all plots have the same axis ranges
    		y_min = -250 
 
    		'''    		      
    		# Plot data (individual days)
    
    		fig1, ax1 = plt.subplots(figsize=(15,8))
    		plt.plot(data_modes['PESR_ALTD'], marker='.', linestyle='None', label='Mode-S pressure altitude')
    		plt.plot(data_amdar['ALTD'], marker='.', color='r', linestyle='None', label='AMDAR pressure altitude')
    		ax1.set_xlabel('Date / time')
    		ax1.set_ylabel('Altitude / m')
    		plt.legend(loc='upper right', prop={'size':8})
    		ax1.set_title('{0} airport - {1}'.format(airport, date))
    		ax1.set_ylim([0, y_max])
    		#ax1.set_xlim([datetime.datetime(2022, 9, 21,9,0,0), datetime.datetime(2022, 9, 21,9,30,0)])
    		ax1.xaxis.set_major_formatter(dates.DateFormatter('%d-%m-%Y %H:%M'))
    		plt.tight_layout()
    		#plt.savefig(os.path.join("D:/Mode-S_altitude/", "{0}_{1}.jpg".format(airport, date)))
    		#plt.show() 
    		plt.close(fig1)
    		'''
        
    	# Plot data (multiple days)



    	start_date_reformat = start_date.strftime('%d-%m-%Y')
    	end_date_reformat = end_date.strftime('%d-%m-%Y')

    	fig2, ax2 = plt.subplots(figsize=(10,6))
    	plt.plot(concat_modes['PESR_ALTD'], marker='.', markersize=2, color ='#1f77b4', linestyle='None', label='Mode-S pressure altitude')
    	plt.plot(concat_amdar['ALTD'], marker='.', markersize=2, color='#d62728', linestyle='None', label='AMDAR pressure altitude')
    	plt.plot(concat_modes_day['PESR_ALTD'], marker='.', color ='#1f77b4', linestyle='--', linewidth=2, label='Mode-S pressure altitude (daily min)')
    	plt.plot(concat_modes_day['GNSS_ALTD'], marker='.', color ='black', linestyle='--', linewidth=2, label='Mode-S GNSS altitude (daily min)')
    	#plt.plot(concat_amdar_day['ALTD'], marker='.', color='#d62728', linestyle='-', linewidth=2, label='AMDAR pressure altitude (daily min)')
    	ax2.set_xlabel('Date / time')
    	ax2.set_ylabel('Altitude / m')
    	plt.legend(loc='upper right', prop={'size':12}, facecolor='white')
    	ax2.set_title('{0} airport '.format(airport)+str(start_date_reformat)+' to '+str(end_date_reformat))
    	ax2.set_ylim([y_min, y_max])
    	ax2.set_xlim([start_date, end_date])
    	ax2.xaxis.set_major_formatter(dates.DateFormatter('%d-%m-%Y'))
    	ax2.axhline(y=0, xmin=0, xmax=1, linewidth =1, linestyle = '--', color='black')
    	ax2.annotate( 'Mean daily min (Mode-S GNSS): ' + str(round(modes_GNSS_mean,0)) , xy = (10,10), xycoords = 'axes points')
    	plt.tight_layout()
    	plt.savefig(os.path.join(out_path, "{0}.jpg".format(airport)))
    	#plt.show() 
    	plt.close(fig2)

    	# Plot hourly minimun altitude data 
  
    	fig3, ax3 = plt.subplots(figsize=(10,6))
    	plt.plot(concat_modes_hour['PESR_ALTD'], marker='.', color ='#1f77b4', linestyle='None', label='Mode-S pressure altitude (hourly min)')
    	plt.plot(concat_modes_hour['GNSS_ALTD'], marker='.', color ='black', linestyle='None', label='Mode-S GNSS altitude (hourly min)')
    	plt.plot(concat_amdar_hour['ALTD'], marker='.', color='#d62728', linestyle='None', label='AMDAR pressure altitude (hourly min)')
    	ax3.set_xlabel('Date / time')
    	ax3.set_ylabel('Altitude / m')
    	plt.legend(loc='upper right', prop={'size':12}, facecolor='white')
    	ax3.set_title('{0} airport (hourly min altd) '.format(airport)+str(start_date_reformat)+' to '+str(end_date_reformat))
    	ax3.set_ylim([y_min, y_max])
    	ax3.set_xlim([start_date, end_date])
    	ax3.xaxis.set_major_formatter(dates.DateFormatter('%d-%m-%Y'))
    	ax3.axhline(y=0, xmin=0, xmax=1, linewidth =1, linestyle = '--', color='black')
    	plt.tight_layout()
    	plt.savefig(os.path.join(out_path, "{0}_hour_min_altd.jpg".format(airport)))
    	#plt.show() 
    	plt.close(fig3)

    	'''   
    	# Average min altitude by hour of day

    	concat_modes_hour = concat_modes_hour.reset_index()
    	concat_modes_hour['hour'] = pd.to_datetime(concat_modes_hour['TIME']).dt.hour
    	concat_modes_hour_avg = pd.DataFrame()
    	for hour in range(0,24,1):
    		hour_filter = concat_modes_hour['hour'] == hour
    		df_hr = pd.DataFrame(concat_modes_hour.loc[hour_filter])
    		concat_modes_hour_avg[hour] = df_hr.mean(axis=0, numeric_only=True)
    	concat_modes_hour_avg = concat_modes_hour_avg.transpose()


    	concat_amdar_hour = concat_amdar_hour.reset_index()
    	concat_amdar_hour['hour'] = pd.to_datetime(concat_amdar_hour['TIME']).dt.hour
    	concat_amdar_hour_avg = pd.DataFrame()
    	for hour in range(0,24,1):
    		hour_filter = concat_amdar_hour['hour'] == hour
    		df_hr = pd.DataFrame(concat_amdar_hour.loc[hour_filter])
    		concat_amdar_hour_avg[hour] = df_hr.mean(axis=0, numeric_only=True)
    	concat_amdar_hour_avg = concat_amdar_hour_avg.transpose()

    	fig4, ax4 = plt.subplots(figsize=(15,8))
    	plt.plot(concat_modes_hour_avg[modes_var], marker='.', linestyle='--', color ='#1f77b4', label='Mode-S (hourly min)')
    	plt.plot(concat_amdar_hour_avg['ALTD'], marker='.', linestyle='--', color='#d62728', label='AMDAR (hourly min)')
    	ax4.set_xlabel('Hour')
    	ax4.set_ylabel('Altitude / m')
    	ax4.set_title('{0} airport (min altd) averaged by hour of day - '.format(airport)+str(start_date)+' to '+str(end_date))
    	plt.xlim(0, 23)
    	plt.xticks(np.arange(0, 24, 2))
    	plt.legend(loc='upper right')
    	plt.tight_layout()
    	plt.savefig(os.path.join(out_path, "{0}_hour_min_altd_AVG.jpg".format(airport)))
    	#plt.show() 
    	plt.close(fig4)
    	'''

    	# Plot daily minimun altitude data 
  
    	fig5, ax5 = plt.subplots(figsize=(10,6))
    	plt.plot(concat_modes_day['PESR_ALTD'], marker='.', color ='#1f77b4', linestyle='-', label='Mode-S pressure altitude (daily min)')
    	plt.plot(concat_modes_day['GNSS_ALTD'], marker='.', color ='black', linestyle='-', label='Mode-S GNSS altitude (daily min)')
    	plt.plot(concat_amdar_day['ALTD'], marker='.', color='#d62728', linestyle='-', label='AMDAR pressure altitude (daily min)')
    	ax5.set_xlabel('Date / time')
    	ax5.set_ylabel('Altitude / m')
    	plt.legend(loc='upper right', prop={'size':12}, facecolor='white')
    	ax5.set_title('{0} airport (daily min altd) '.format(airport)+str(start_date_reformat)+' to '+str(end_date_reformat))
    	ax5.set_ylim([y_min, y_max])
    	ax5.set_xlim([start_date, end_date])
    	ax5.xaxis.set_major_formatter(dates.DateFormatter('%d-%m-%Y'))
    	ax5.axhline(y=0, xmin=0, xmax=1, linewidth =1, linestyle = '--', color='black')
    	ax5.annotate( 'Mean daily min (Mode-S GNSS): ' + str(round(modes_GNSS_mean,0)) , xy = (10,40), xycoords = 'axes points')
    	ax5.annotate( 'Mean daily min (Mode-S pressure): ' + str(round(modes_pressure_mean,0)), xy = (10,25), xycoords = 'axes points')
    	ax5.annotate( 'Mean daily min (AMDAR pressure): ' + str(round(amdar_pressure_mean,0)), xy = (10,10), xycoords = 'axes points')
    	plt.tight_layout()
    	plt.savefig(os.path.join(out_path, "{0}_day_min_altd.jpg".format(airport)))
    	#plt.show() 
    	plt.close(fig5)


if __name__ == '__main__':
    main()


