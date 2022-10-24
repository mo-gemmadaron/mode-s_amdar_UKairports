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

def load_day_min(file_path, airport, period):

    filename = '{0}/{1}_{2}_day_min_BG.csv'.format(file_path, airport, period) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    data['TIME'] = pd.to_datetime(data['TIME'], format='%Y%m%d')

    data.set_index('TIME', inplace=True)


    return(data)


def main():

    # load locations file
    file_path = '/data/users/gdaron/Mode-S_altitude/Mode-S_day_min'
    out_path = '/data/users/gdaron/Mode-S_altitude/Mode-S_day_min/plots'

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    # load NETCDF4 file
    fn = '/data/users/gdaron/Mode-S_altitude/Min_obs_altd_existing/constant_ng_network_Existing_deriv.nc'
    ds = nc.Dataset(fn, 'r')

    xcellsize = 1000
    ycellsize = 1000

    # select period
    period = 'summer' # 'summer' or 'winter'

    if period == 'summer':
        start_date = datetime.date(2021,7,10)
        end_date = datetime.date(2021,8,10)

    if period == 'winter':
        start_date = datetime.date(2022,1,1)
        end_date = datetime.date(2022,1,31)
    

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
    
    for airport in airport_name_list:

    	data = load_day_min(file_path, airport, period)
    	print(data)

    	# Loop through locations and extract minimum observable height value
    	for idx, row in data.iterrows():
    		point_lat = row['LAT']
    		point_lon = row['LON']

    		lat = ds.variables['latitude'][:]
    		nrows = lat.size
    		min_lat = np.amin(lat)
    		max_lat = np.amax(lat)

    		lon = ds.variables['longitude'][:]
    		ncols = lon.size
    		min_lon = np.amin(lon)
    		max_lon = np.amax(lon)

    		# Locate pixel
    		px = int((point_lon - min_lon) / xcellsize)
    		py = int((point_lat - min_lat) / ycellsize)

    		lowest_beam_height_amsl = ds.variables['lowest_beam_height_amsl'][:]
    		data.loc[idx,'min_obs_altd'] = lowest_beam_height_amsl[py, px]

    	print(data)


    	# Plot data (multiple days)

    	start_date_reformat = start_date.strftime('%d/%m/%Y')
    	end_date_reformat = end_date.strftime('%d/%m/%Y')

    	fig1, ax1 = plt.subplots(figsize=(6,6))
    	plt.plot(data['GNSS_ALTD'], marker='.', markersize=3, color ='#1f77b4', linestyle='-', label='Mode-S observed daily minimum')
    	plt.plot(data['min_obs_altd'], marker='.', markersize=3, color='#d62728', linestyle='-', label='Model')

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
    	plt.savefig(os.path.join(out_path, "{0}_{1}_day_min.jpg".format(airport, period)))
    	#plt.show() 
    	plt.close(fig1)
'''

    fn = '/data/users/gdaron/Mode-S_altitude/Min_obs_altd_existing/constant_ng_network_Existing_deriv.nc'
    ds = nc.Dataset(fn, 'r')

    point_lat = 179887
    point_lon = 542388

    #print(ds)
    #print(ds.__dict__)

    #for dim in ds.dimensions.values():
    	#print(dim)

    #for var in ds.variables.values():
    	#print(var)

    #print(ds['lowest_beam_height_amsl'])

    lat = ds.variables['latitude'][:]
    nrows = lat.size
    min_lat = np.amin(lat)
    max_lat = np.amax(lat)

    lon = ds.variables['longitude'][:]
    ncols = lon.size
    min_lon = np.amin(lon)
    max_lon = np.amax(lon)

    #xcellsize = (max_lon - min_lon) / ncols
    #ycellsize = (max_lat - min_lat) / nrows
    xcellsize = 1000
    ycellsize = 1000
    #print(xcellsize)
    #print(ycellsize)
    px = int((point_lon - min_lon) / xcellsize)
    py = int((point_lat - min_lat) / ycellsize)
    print(px)
    print(py)


    lowest_beam_height_amsl = ds.variables['lowest_beam_height_amsl'][:]
    #print(lowest_beam_height_amsl)
    #print(lowest_beam_height_amsl.size)
    print(lowest_beam_height_amsl[py, px]) # latitude, longitude

'''

if __name__ == '__main__':
    main()


