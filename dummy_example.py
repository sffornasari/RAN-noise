#Dummy exemple
import obspy
#import numpy as np
from ppsd_dmg import PPSD
#import matplotlib.pyplot as plt
import datetime
#import scipy
import glob


sta = 'ABC'
year = 2022
jday = 19

filenames = glob.glob(f'{sta}*{year}.{jday:03d}*') 

#Prepare the data 
st = obspy.read(filenames[0])
stime = obspy.UTCDateTime(st.traces[0].stats.starttime.date.strftime('%Y-%m-%dT%H:%M:%S'))
etime = obspy.UTCDateTime((st.traces[0].stats.starttime.date+datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S'))
for filename in filenames[1:]:
    st += obspy.read(filename)
st.merge()
if st.traces[0].stats.starttime.hour > 0:
    try:
        prev_day = glob.glob(f'{sta}*{year}.{(jday-1):03d}*') 
        st += obspy.read(prev_day[-1])
        st.merge()
    except:
        print('Initial gap: no data retrieved from the previous day.')
        pass
#This part is NOT error-proof!!!
st.trim(starttime= stime,
    endtime=etime,
    pad=True,
    )
tr = st.traces[0]
#Convert from nm/s**2 to m/s**2
tr.data = tr.data*1e-9


#Read the station metadata
inv = obspy.read_inventory(f"{filenames[0].split('.')[0]}.xml")
   

#Compute the PSDs
ppsd = PPSD(stats=tr.stats, metadata=inv, skip_on_gaps=False,
                db_bins=(-200, -50, 1.), ppsd_length=90*60.0, overlap=0.5, winparams='hann',
                special_handling="accelerometer", smoothing=False, period_smoothing_width_octaves=1.0,
                subchunk_fraction = 0.25, subchunk_overlap_fraction = 0.75,
                period_step_octaves=0.125, period_limits=None)


ppsd.add(tr)

#Save results
ppsd.save_npz_min()
