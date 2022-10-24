#!/usr/bin/env python3.8
# -*- coding: iso-8859-1 -*-

'''
compare_modes_model.py

Code to extract the model "minimum observable altitude" from netCDF files and compare with daily minimum observations

To run the code:
   ./compare_modes_model.py

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
import netCDF4 as nc



def load_day_min(file_path_day_min, airport, period):

    filename = '{0}/{1}_{2}_day_min_BG.csv'.format(file_path_day_min, airport, period) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    data['TIME'] = pd.to_datetime(data['TIME'], format='%Y%m%d')

    data.set_index('TIME', inplace=True)

    return(data)


def load_netcdf(file_path_netcdf, scenario):

    filename = '{0}/constant_ng_network_{1}_deriv.nc'.format(file_path_netcdf, scenario) 

    if not os.path.isfile(filename):
        return -1

    data = nc.Dataset(filename, 'r')

    return(data)


def extract_model_data(netcdf_file, point_lon, point_lat, xcellsize, ycellsize):

    lat = netcdf_file.variables['latitude'][:]
    nrows = lat.size
    min_lat = np.amin(lat)
    max_lat = np.amax(lat)

    lon = netcdf_file.variables['longitude'][:]
    ncols = lon.size
    min_lon = np.amin(lon)
    max_lon = np.amax(lon)

    px = int((point_lon - min_lon) / xcellsize)
    py = int((point_lat - min_lat) / ycellsize)

    lowest_beam_height = netcdf_file.variables['lowest_beam_height_amsl'][:]

    return lowest_beam_height, px, py


def main():

    # 1. Set paths
    file_path_day_min = '/data/users/gdaron/Mode-S_altitude/Mode-S_day_min'

    file_path_netcdf = '/data/users/gdaron/Mode-S_altitude/Min_obs_altd/'

    out_path_plots = '/data/users/gdaron/Mode-S_altitude/Mode-S_day_min/plots'
    if not os.path.exists(out_path_plots):
        os.makedirs(out_path_plots)


    # 2. Load NETCDF files
    ds_exist = load_netcdf(file_path_netcdf, 'Existing')
    ds_all = load_netcdf(file_path_netcdf, 'AllSites')


    # 3. Select period
    period = 'summer' # 'summer' or 'winter'

    if period == 'summer':
        start_date = datetime.date(2021,7,10)
        end_date = datetime.date(2021,8,10)

    if period == 'winter':
        start_date = datetime.date(2022,1,1)
        end_date = datetime.date(2022,1,31)

    
    # 4. Select airports
    airport_name_list = ['Bristol']
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

    # 5. Loop through airports and extract model data
    for airport in airport_name_list:

    	data_day_min = load_day_min(file_path_day_min, airport, period)

    	for idx, row in data_day_min.iterrows():
    		point_lat = row['LAT']
    		point_lon = row['LON']

    		# Existing network
    		lowest_beam_height_exist, px, py = extract_model_data(ds_exist, point_lon, point_lat, 1000, 1000)
    		data_day_min.loc[idx,'min_obs_altd_exist'] = lowest_beam_height_exist[py, px]

    		# AllSites network
    		lowest_beam_height_all, px, py = extract_model_data(ds_all, point_lon, point_lat, 1000, 1000)
    		data_day_min.loc[idx,'min_obs_altd_all'] = lowest_beam_height_all[py, px]

    	print(data_day_min)


    	# Plot data (multiple days)

    	start_date_reformat = start_date.strftime('%d/%m/%Y')
    	end_date_reformat = end_date.strftime('%d/%m/%Y')

    	fig1, ax1 = plt.subplots(figsize=(6,6))
    	plt.plot(data_day_min['GNSS_ALTD'], marker='.', markersize=3, color ='#1f77b4', linestyle='-', label='Mode-S observed daily minimum')
    	plt.plot(data_day_min['min_obs_altd_exist'], marker='.', markersize=3, color='#ff7f0e', linestyle='-', label='Model (existing network)')
    	plt.plot(data_day_min['min_obs_altd_all'], marker='.', markersize=3, color='#2ca02c', linestyle='-', label='Model (full network)')

    	ax1.set_title('{0} airport - {1} '.format(airport, period))
    	ax1.set_xlabel('Date')
    	ax1.set_xlim([start_date, end_date])
    	ax1.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
    	#ax1.xaxis.set_major_locator(dates.DayLocator(interval=7))
    	ax1.set_xticks(np.arange(start_date, end_date, 7))

    	ax1.set_ylabel('Altitude / m')
    	ax1.set_ylim([-250, 3000])

    	plt.legend(loc='upper right', prop={'size':12}, facecolor='white')
    	ax1.axhline(y=0, xmin=0, xmax=1, linewidth =1, linestyle = '--', color='black')
    	#ax1.annotate( 'Mean daily min (Mode-S GNSS): ' + str(round(modes_GNSS_mean,0)) , xy = (10,10), xycoords = 'axes points')
    	plt.tight_layout()
    	plt.savefig(os.path.join(out_path_plots, "{0}_{1}_day_min.jpg".format(airport, period)))
    	#plt.show() 
    	plt.close(fig1)


if __name__ == '__main__':
    main()


