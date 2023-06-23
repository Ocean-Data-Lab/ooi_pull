import os
import sys

#cwd = os.getcwd()
#ooipy_dir = os.path.dirname(cwd) + '/ooipy'
#sys.path.append(ooipy_dir)

from matplotlib import pyplot as plt
import datetime
import numpy as np
from obspy import read,Stream, Trace
from obspy.core import UTCDateTime

from obspy import read
import pickle
import scipy
from gwpy.timeseries import TimeSeries
import seaborn as sns

from ooipy.request import hydrophone_request
import gwpy

from datetime import timedelta

import xarray

nodes = ['Axial_Base', 'Central_Caldera','Eastern_Caldera','Frequency','Slope_Base','Southern_Hydrate']
years = [2015, 2016, 2017, 2018, 2019, 2022] # Add 2023 for full year

master_file_names = []

kstart=0

for node_count, node in enumerate(nodes):
    for year_count, year in enumerate(years):
        start_time_first = datetime.datetime(year,1,1,0,0,0)
        
        # set num of hours in year depending on leap
        if (year % 4) == 0:
            num_hours = 8784
        else:
            num_hours = 8760

        if (node_count == 0) & (year_count==0):
            start_index = kstart
        else:
            start_index = 0
        for k in range(start_index,num_hours):
            start_time = start_time_first + timedelta(hours=k)
            end_time = start_time_first + timedelta(hours=k+1)
            print(f'Computing Spectrogram for {node} | {start_time} - {end_time}: {k}')
            print('   Downloading Data...')
            hdata = hydrophone_request.get_acoustic_data_LF(start_time, end_time, node, channel='HNZ')
            print('   Computing Spectrogram...')
            try:
                # 1 minute average PSD
                spec = hdata.compute_spectrogram(avg_time=60, L=512, average_type='mean')
            except:
                print('   No Data for time segment')
                spec = None
            print('   Writing to File...')

            # Write to Pickle File
            # Adjust filename to work with local machine's directories
            filename = "/Volumes/Ocean_Acoustics/Spectrograms/seismometers/" +node+ "/" + str(year) +f"/spectrogram{k:03}.pkl"
            with open(filename,'wb') as f:
                pickle.dump(spec, f)
            master_file_names.append(filename)


## Part 2 - Converting data to zarr files

## Iterates over files, reads pkl data (dictonary). Then, creates an xarray object for the data
## and makes it into a zarr file using the method: to_zarr. 
for i in master_file_names:
    with open(i, 'r') as f: 
        data = pickle.load(f)
        temp = xarray.data.to_xarray()
        xarray.temp.to_zarr(append_dim="")  # append_dim to add to same diretory



