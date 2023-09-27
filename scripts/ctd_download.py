import ooipy
import datetime
from matplotlib import pyplot as plt
import pandas as pd
from tqdm import tqdm
import pickle

# If you get an authentication error, you need to set your OOI_username and OOI_token as environment variables.
# and also to update to latest version of ooipy
start_day = pd.Timestamp('2023-01-01')
end_day = pd.Timestamp('2023-04-18')
n_days = (end_day - start_day).days

for k in tqdm(range(n_days)):
    day = (start_day + pd.Timedelta(days=k)).to_pydatetime()
    ctddata = ooipy.request.ctd_request.get_ctd_data_daily(day, location='axial_base', only_profilers=True)
    profile = ctddata.get_profile(3000, parameter='sound_speed')

    fn = f'/Volumes/Ocean_Acoustics/CTD_Data_ooipy/only_profilers/axial_base/{day.strftime("%Y-%m-%d.pkl")}'
    with open(fn, 'wb') as f:
        pickle.dump(profile, f)
    