#!/usr/bin/env python3.8
# -*- coding: iso-8859-1 -*-

'''
test_geopandas.py

Test shape files etc...

To run the code:
   ./test_geopandas.py

Author: gdaron
'''

import shapely
import geopandas as gpd
import csv
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import dates
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)


def import_mode_s_files(file_path, date):

    filename = '{0}/MODE-S_{1}.txt'.format(file_path, date) 

    if not os.path.isfile(filename):
        return -1

    mode_s_file = pd.read_csv(filename)
    mode_s_file["TIME"] = pd.to_datetime(mode_s_file["TIME"], format="%Y%m%d%H%M")

    return(mode_s_file)


def import_amdar_files(file_path, date):

    filename = '{0}/AMDARS_{1}.txt'.format(file_path, date) 

    if not os.path.isfile(filename):
        return -1

    amdar_file = pd.read_csv(filename)
    amdar_file["TIME"] = pd.to_datetime(amdar_file["TIME"], format="%Y%m%d%H%M")

    return(amdar_file)


def get_dates_list(file_path):

    file_list = os.listdir(file_path)

    dates_list = []

    for file in file_list:
    	if file.endswith('text_RAD16_qpe_azimuth_stats'):
    		date_str = file.partition('_')[0]
    		dates_list.append(date_str)
    dates_list.sort()
    return(dates_list)


def compile_azimuth_data(file_path, dates_list, parameter):

    compile_df = pd.DataFrame(index = pd.RangeIndex(start=0.0, stop=360.0, step=1.0))

    for date in dates_list:

    	data_df = import_azimuth_files(file_path, date)

    	data_df.set_index('Azimuth', inplace=True)

    	data_df.rename(columns = {parameter : parameter+'_'+date}, inplace = True) # rename columns to prevent duplication when merging

    	compile_df = pd.merge(compile_df, data_df[parameter+'_'+date], left_index = True, right_index = True, how = 'inner')
 
    compile_df.columns = dates_list

    compile_df['mean'] = compile_df.mean(axis=1)

    return(compile_df)


def main():

    '''
    file_path_mode_s = '/data/users/gdaron/MetDB/MODE-S/202209261006/'

    data_mode_s = import_mode_s_files(file_path_mode_s, '20220919')
    data_mode_s.set_index('TIME', inplace=True)
    print(data_mode_s)

    file_path_amdar = '/data/users/gdaron/MetDB/AMDARS/202209261005/'

    data_amdar = import_amdar_files(file_path_amdar, '20220919')
    data_amdar.set_index('TIME', inplace=True)
    print(data_amdar)

    out_path = '/data/users/gdaron/Mode-S_altitude/'

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    plt.plot(data_mode_s['GNSS_ALTD'], marker='.', linestyle='None', label='Mode-S')
    plt.plot(data_amdar['ALTD'], marker='.', color='r', linestyle='None', label='AMDAR')
    ax1.set_xlabel('Date / time')
    #ax1.xaxis.set_major_formatter(dates.DateFormatter('%d:%m:%y %H:%M'))
    ax1.set_ylabel('Altitude / m')
    plt.legend(loc='upper left', prop={'size':8})
    ax1.set_title('Bristol airport - 20220919')
    plt.tight_layout()
    plt.savefig(os.path.join(out_path, 'Bristol_20220919_test.png'))
    plt.show()




    fig1, ax1 = plt.subplots(figsize=(10, 6))
    for col, c in zip(compile_df.columns, color):
    	if col == 'mean':
    		compile_df[col].plot(label=f'{col}', linewidth =1.5, color='black')
    	else:
    		compile_df[col].plot(label=f'{col}', linewidth =1.0, color=c)
    ax1.set_xlabel('Azimuth / deg')




    #out_path = '/data/users/gdaron/cobbacombe/azimuth_variations/qpe_diag/plots'

    #if not os.path.exists(out_path):
        #os.makedirs(out_path)

    #2. Get list of dates 

    #dates_list = get_dates_list(file_path)

    #3. Loop through params and produce azimuth plots

    params_list = ['Detect', 'Accum', 'Avg.']

    for parameter in params_list:

    	compile_df = compile_azimuth_data(file_path, dates_list, parameter)

    	## FIGURE 1 - plots of azimuth variation in probability, accumulation and precip rate by month

    	# Generate colour map
    	color = cm.tab20(np.linspace(0, 1, len(dates_list)+1))
     
    	fig1, ax1 = plt.subplots(figsize=(10, 6))
    	for col, c in zip(compile_df.columns, color):
    		if col == 'mean':
    			compile_df[col].plot(label=f'{col}', linewidth =1.5, color='black')
    		else:
    			compile_df[col].plot(label=f'{col}', linewidth =1.0, color=c)
    	ax1.set_xlabel('Azimuth / deg')

    	if parameter == 'Detect':
    		ax1.set_ylabel('Probability of precipitation / %')
    		ax1.set_title('Cobbacombe Cross - Probability of precipitation')
    	if parameter == 'Accum':
    		ax1.set_ylabel('Precipitation accumulation / mm')
    		ax1.set_title('Cobbacombe Cross - Precipitation accumulation')
    	if parameter == 'Avg.':
    		ax1.set_ylabel('Average precipitation rate / mm/hr')
    		ax1.set_title('Cobbacombe Cross - Average precipitation rate')

    	ax1.set_xlim([0, 359])
    	plt.legend(ncol=2, loc='upper left', prop={'size':8}, title='YYYYmm')

    	ax1.xaxis.set_major_locator(MultipleLocator(10))
    	ax1.xaxis.set_major_formatter('{x: .0f}')
    	plt.xticks(np.arange(0, 359, 10), rotation=90)
    	ax1.xaxis.set_minor_locator(MultipleLocator(1))

    	ax1.grid(which='major', linewidth=1)
    	ax1.grid(which='minor', linewidth=0.5, linestyle='--')

    	plt.tight_layout()
    	plt.savefig(os.path.join(out_path, 'RAD16_qpe_azimuth_stats_{0}.png'.format(parameter)))
    	plt.close(fig1)

    	## FIGURE 2 - 
    	#Load and compare example horizon files derived from tree heights

    	scenarios_list = ['Elevation_angle', 'Elevation_angle_1m', 'Elevation_angle_2m', 'Elevation_angle_3m', 'Elevation_angle_4m']

    	for scenario in scenarios_list:

    		horizon_file = import_horizon_files(scenario)

    		fig2, ax2 = plt.subplots(figsize=(10, 6))
    		for col, c in zip(compile_df.columns, color):
    			if col == 'mean':
    				compile_df[col].plot(label=f'{col}', linewidth =1.5, color='black')
    			else:
    				compile_df[col].plot(label=f'{col}', linewidth =1.0, color=c)
    		ax2.set_xlabel('Azimuth / deg')

    		if parameter == 'Detect':
    			ax2.set_ylabel('Probability of precipitation / %')
    			ax2.set_title('Cobbacombe Cross - Probability of precipitation + horizon file ({0})'.format(scenario))
    		if parameter == 'Accum':
    			ax2.set_ylabel('Precipitation accumulation / mm')
    			ax2.set_title('Cobbacombe Cross - Precipitation accumulation + horizon file ({0})'.format(scenario))
    		if parameter == 'Avg.':
    			ax2.set_ylabel('Average precipitation rate / mm/hr')
    			ax2.set_title('Cobbacombe Cross - Average precipitation rate + horizon file ({0})'.format(scenario))

    		ax2.set_xlim([0, 359])
    		plt.legend(ncol=2, loc='upper left', prop={'size':8}, title='YYYYmm')

    		ax2.xaxis.set_major_locator(MultipleLocator(10))
    		ax2.xaxis.set_major_formatter('{x: .0f}')
    		plt.xticks(np.arange(0, 359, 10), rotation=90)
    		ax2.xaxis.set_minor_locator(MultipleLocator(1))

    		ax2.grid(which='major', linewidth=1)
    		ax2.grid(which='minor', linewidth=0.5, linestyle='--')

    		ax3 = ax2.twinx()
    		plt.bar(horizon_file['azimuth_round'],horizon_file[scenario], color = 'gray', alpha = 0.5)
    		ax3.set_ylabel('Horizon angle / deg')
    		ax3.set_ylim([0, 6])

    		plt.tight_layout()

    		out_path_fig2 = out_path + '/horizons'

    		if not os.path.exists(out_path_fig2):
        		os.makedirs(out_path_fig2)

    		plt.savefig(os.path.join(out_path_fig2, 'RAD16_qpe_azimuth_stats_{0}_{1}.png'.format(parameter, scenario)))
    		plt.close(fig2)


    '''

if __name__ == '__main__':
    main()


