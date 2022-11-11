#!/usr/bin/env python3.8
# -*- coding: iso-8859-1 -*-

'''
create_bar_chart.py

create bar chart comparing the minimum observed Mode-S altitude with the model

To run the code:
   ./create_bar_chart.py

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


def load_stats_file(file_path_stats, period):

    filename = '{0}/Airport_min_mode-s_stats_{1}.csv'.format(file_path_stats, period) 

    if not os.path.isfile(filename):
        return -1

    data = pd.read_csv(filename)

    data.rename(columns = {'Unnamed: 0':'Airport'}, inplace = True)

    data.set_index('Airport', inplace=True)

    return(data)


def main():

    # 1. Set paths
    file_path_stats = '/data/users/gdaron/Mode-S_altitude/Mode-S_day_min/outputs'

    period_list = ['winter', 'summer']

    # 2. Load data

    data_winter = load_stats_file(file_path_stats, 'winter')
    data_summer = load_stats_file(file_path_stats, 'summer')

    # 3. Remove winter data at London airports (affected by Thurham outage)

    data_winter.loc[['Heathrow', 'Gatwick', 'Stansted', 'LondonCity']] = np.nan

    # 4. Average across winter and summer periods

    df_concat = pd.concat([data_summer, data_winter])
    by_row_index = df_concat.groupby(df_concat.index)
    df_means = by_row_index.mean()

    df_means.reset_index(inplace=True)

    wd = 0.3

    '''
    #this works for one plot
    for index, row in df_means.iterrows():
    	airport = df_means.loc[index, 'Airport']
    	fig1, ax1 = plt.subplots(figsize=(6,6))
    	plt.bar(0, df_means.loc[index, 'GNSS_ALTD'], color='#1f77b4', width=wd, edgecolor='k',label='Mode-S observed daily minimum')
    	plt.bar(0+wd, df_means.loc[index, 'min_obs_altd_exist'], color='#ff7f0e', width=wd, edgecolor='k', label='Model (existing network)')
    	plt.bar(0+(2*wd), df_means.loc[index, 'min_obs_altd_priority'], color='#2ca02c', width=wd, edgecolor='k', label='Model (priority network)')
    	plt.bar(0+(3*wd), df_means.loc[index, 'min_obs_altd_all'], color='#9467bd', width=wd, edgecolor='k', label='Model (full network)')
    	plt.tick_params(axis='x', which='both', bottom=False, labelbottom=False)

    	ax1.set_xlabel('{0}'.format(airport))
    	ax1.set_ylabel('Altitude / m')
    	ax1.set_ylim([0, 2000])
    	plt.tight_layout()
    	plt.show()
    '''

    # test subplots
    fig2, ax2 = plt.subplots(4,4,figsize=(10,12))
    plt.subplots_adjust(hspace=0.5, wspace=0.5)
    for index, row in df_means.iterrows():
    	airport = df_means.loc[index, 'Airport']
    	ax2 = plt.subplot(4, 4, index+1)
    	plot1=plt.bar(0, df_means.loc[index, 'GNSS_ALTD'], color='#1f77b4', width=wd, edgecolor='black',label='Mode-S observed daily minimum')
    	plot2=plt.bar(0+wd, df_means.loc[index, 'min_obs_altd_exist'], color='#ff7f0e', width=wd, edgecolor='black', label='Model (existing network)')
    	plot3=plt.bar(0+(2*wd), df_means.loc[index, 'min_obs_altd_priority'], color='#2ca02c', width=wd, edgecolor='black', label='Model (priority network)')
    	plot4=plt.bar(0+(3*wd), df_means.loc[index, 'min_obs_altd_all'], color='#9467bd', width=wd, edgecolor='black', label='Model (full network)')
    	plt.tick_params(axis='x', which='both', bottom=False, labelbottom=False)

    	ax2.set_xlabel('{0}'.format(airport))
    	ax2.set_ylabel('Altitude / m')
    	ax2.set_ylim([0, 2000])

    labels = ['Mode-S observed daily minimum','Model (existing network)','Model (priority network)','Model (full network)']  	
    fig2.legend([plot1, plot2, plot3, plot4], bbox_to_anchor=(0.5,0.98), loc='center', prop={'size':10}, labels=labels, ncol = 4)
    fig2.suptitle('test', fontweight = 'bold', y= 1.0, color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(file_path_stats, "Bar_chart_for_report.jpg"))
    #plt.show()





if __name__ == '__main__':
    main()


