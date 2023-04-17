import ooipy
import datetime
from matplotlib import pyplot as plt
import pandas as pd
from tqdm import tqdm
import pickle

#TODO add ability to read username and token from environment variables
USERNAME = <OOI_USERNAME>
TOKEN = <OOI_TOKEN>
ooipy.request.authentification.set_authentification(USERNAME, TOKEN)

start_day = pd.Timestamp('2021-01-02')

for k in tqdm(range(365*2 - 1)):
    day = (start_day + pd.Timedelta(days=k)).to_pydatetime()
    ctddata = ooipy.request.ctd_request.get_ctd_data_daily(day, location='axial_base', only_profilers=True)
    profile = ctddata.get_profile(3000, parameter='sound_speed')

    fn = f'/Volumes/Ocean_Acoustics/CTD_Data_ooipy/only_profilers/axial_base/{day.strftime("%Y-%m-%d.pkl")}'
    with open(fn, 'wb') as f:
        pickle.dump(profile, f)
    