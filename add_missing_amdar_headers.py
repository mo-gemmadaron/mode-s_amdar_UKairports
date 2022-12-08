#!/usr/bin/env python3.8
# -*- coding: iso-8859-1 -*-

'''
add_missing_amdar_headers.py

Code for adding missing headers to the amdar metdb outputs 

To run the code:
   ./add_missing_amdar_headers.py

Author: gdaron
'''

import sys, os
import os.path as path
import fileinput

src_extensions = ['.txt']

def is_src_file(f):
    results = [f.endswith(ext) for ext in src_extensions]
    return True in results

def is_header_missing(f):
    with open(f) as reader:
        lines = reader.read().lstrip().splitlines()
        #if len(lines) > 0: return not lines[0].startswith("/**")
        if len(lines) > 0: return not lines[0].startswith("RGSN")
        if len(lines) == 0: return True
        return True

def get_src_files(dirname):
    src_files = []
    for cur, _dirs, files in os.walk(dirname):
        [src_files.append(path.join(cur,f)) for f in files if is_src_file(f)]

    return [f for f in src_files if is_header_missing(f)]

def add_headers(files, header):
    for line in fileinput.input(files, inplace=True):
        if fileinput.isfirstline():
            [ print(h) for h in header.splitlines() ]
        print(line, end="")



if __name__ == "__main__":

    airport_name_list = ['Cardiff']
    
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

    for airport in airport_name_list:

    	root_path = '/data/users/gdaron/Mode-S_altitude/MetDB_extract/AMDARS/{0}'.format(airport)

    	header = "RGSN_NMBR,TIME,LAT,LON,ALTD" 
    	files = get_src_files(root_path)

    	print("Files with missing headers:")
    	[print("  - %s" % f) for f in files]

    	print()
    	print("Header: ")
    	print(header)

    	for f in files:
    		filesize = os.path.getsize(f)
    		if filesize == 0:
    			with open(f, 'a') as file_writer:
    				file_writer.write(header + "\n")
    				file_writer.close

    	files = get_src_files(root_path)

    	if len(files)!= 0:
    		add_headers(files, header)



