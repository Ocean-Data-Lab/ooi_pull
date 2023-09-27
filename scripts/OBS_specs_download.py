import ooipy
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import datetime
from tqdm import tqdm
import os

lf_nodes = ['AXAS1', 'AXAS2', 'AXBA1', 'AXCC1', 'AXEC1', 'AXEC2', 'AXEC3', 'AXID1', 'HYS11', 'HYS12', 'HYS13', 'HYS14', 'HYSB1']
cal = [8.44986E8, 8.44986E8, 9.07909E8, 9.24794E8, 8.44986E8, 9.24587E8, 8.44986E8, 8.44986E8, 8.44986E8, 8.44986E8, 8.44986E8, 9.22982E8, 9.21043E8]
lfhyd_nodes = ['AXBA1','AXCC1','AXEC2','HYS14','HYSB1']

# construct list of lf devices (hydrophones and seismometers)
obss = {}
for k, node in enumerate(lf_nodes):
    if node in lfhyd_nodes:
        obss[node] = {'channel':'HHZ', 'cal':cal[k]}
    else:
        obss[node] = {'channel':'EHZ', 'cal':cal[k]}
        
day = datetime.datetime(2015,1,1,0)

while day < datetime.datetime(2023,1,1):
    fn = f'/Volumes/Ocean_Acoustics/OOI_OBS_specs/{day.strftime("%Y%m%d")}.nc'
    if os.path.exists(fn):
        day = day + datetime.timedelta(days=1)
        continue
    print(f'downloading data for {day}...')
    Sxs_day = []
    nperseg=2048
    f_coord = np.linspace(0,100,int(nperseg/2)+1)

    for k in tqdm(range(24)):
        starttime = day + datetime.timedelta(hours=k)
        endtime = day + datetime.timedelta(hours=k+1)
        Sxs = {}

        for obs in obss:
            hdata = ooipy.get_acoustic_data_LF(starttime, endtime, node=obs, channel=obss[obs]['channel'], verbose=False)
            if hdata is not None:
                data_cal = hdata.data/obss[obs]['cal']
                # if less than 1/4 of data is present, throw out
                if len(data_cal) < 180e3:
                    data_cal = None
            else:
                data_cal = None

            if data_cal is not None:
                _,S = signal.welch(data_cal, fs=200, nperseg=2048, average='median', scaling='density')
                Sxs[obs] = xr.DataArray(
                    20*np.log10(np.expand_dims(S, axis=0)),
                    dims=['time', 'frequency'],
                    coords={'time':[starttime], 'frequency':f_coord},
                    name=obs, 
                    attrs={'units':'dB rel 1 $(m/s)^2/Hz$'}
                )        
            else:
                Sxs[obs] = xr.DataArray(
                    np.ones((1, 1025))*np.nan,
                    dims=['time', 'frequency'],
                    coords={'time':[starttime], 'frequency':f_coord},
                    name=obs,
                    attrs={'units':'dB rel 1 $(m/s)^2/Hz$'}
                )   
        Sxs_day.append(xr.Dataset(Sxs))
    specs_day = xr.concat(Sxs_day, dim='time')

    specs_day.to_netcdf(fn)
    day = day + datetime.timedelta(days=1)