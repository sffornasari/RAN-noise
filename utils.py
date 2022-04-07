#Utility functions for PSDs computation
import os
import obspy
import numpy as np
import pandas as pd
from ppsd_dmg import PPSD
import datetime
import scipy
import glob
from multiprocessing import Pool, Queue, Process, Value, Manager, current_process
from functools import partial
import time
import logging

def onestation_psd(sta, cha, year, jdaymin, jdaymax=None, wfpath='.', invpath='.', outpath='.', extsearch=False):
    worknumber = current_process().name
    jdaymin = int(jdaymin)
    if jdaymax == None:
        jdaymax = jdaymin
    jdaymax = int(jdaymax)
    
    #Read the station metadata
    invfile = glob.glob(f"{invpath}/{sta}.xml")
    if not invfile:
        return
    inv = obspy.read_inventory(invfile[0])
    for chan in inv._networks[0]._stations[0].channels:
        chan._code = chan.code[0] + 'N' + chan.code[-1]
        
    #For each day in the range yearjdaymin-yearjdaymax
    for jday in range(jdaymin, jdaymax+1):
        try:
            #Check if already processed
            if glob.glob(f'{outpath}/{sta}.{cha}_{year}_{jday:03d}.npz'):
                logging.debug(f'Worker-{worknumber} -> {sta} Already processed.')
                continue
            filenames = glob.glob(f'{wfpath}/{year}/{year}_*/{year}/{jday:03d}/{sta}.{cha}.{year}.{jday:03d}')
            #filenames = glob.glob(f'{wfpath}/{sta}*{cha}*{year}.{jday:03d}*')
            if not filenames:
                continue
            #Prepare the data 
            st = obspy.read(filenames[0])
            stime = obspy.UTCDateTime(st.traces[0].stats.starttime.date.strftime('%Y-%m-%dT%H:%M:%S'))
            etime = obspy.UTCDateTime((st.traces[0].stats.starttime.date+datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S'))
            try:
                inv.get_response(st.traces[0].get_id(), stime)
            except Exception as e:
                logging.debug(f'Worker-{worknumber} -> {sta} Response missing: {e}')
                return
            for filename in filenames[1:]:
                st += obspy.read(filename)
            st.merge()
            if extsearch == True:
                if st.traces[0].stats.starttime.hour > 0 and st.traces[0].stats.endtime.minute > 1:
                    try:
                        prev_day = glob.glob(f'{wfpath}/{year}/{year}_*/{year}/{(jday-1):03d}/{sta}.{cha}.{year}.{(jday-1):03d}')
                        st += obspy.read(prev_day[-1])
                        st.merge()
                    except:
                        logging.debug(f'Worker-{worknumber} -> {sta} Initial gap: no data retrieved from the previous day.')
                        pass
                if st.traces[0].stats.endtime.hour < 23 and st.traces[0].stats.endtime.minute < 59:
                    try:
                        next_day = glob.glob(f'{wfpath}/{year}/{year}_*/{year}/{(jday+1):03d}/{sta}.{cha}.{year}.{(jday+1):03d}')
                        st += obspy.read(next_day[0])
                        st.merge()
                    except:
                        logging.debug(f'Worker-{worknumber} -> {sta} Final gap: no data retrieved from the next day.')
                        pass
            #This part is NOT error-proof!!!
            st.trim(starttime= stime,
                endtime=etime,
                pad=True,
                )
            tr = st.traces[0]
            #Convert from nm/s**2 to m/s**2
            tr.data = tr.data*1e-9
        except Exception as e:
            logging.debug(f"Worker-{worknumber} -> {sta} waveform problem: {e}")
            continue
        try:
            #Initialize PSD-computing class
            ppsd = PPSD(stats=tr.stats, metadata=inv, skip_on_gaps=False,
                            db_bins=(-200, -50, 1.), ppsd_length=90*60.0, overlap=0.5, winparams='hann',
                            special_handling="accelerometer", smoothing=False, period_smoothing_width_octaves=1.0,
                            subchunk_fraction = 0.25, subchunk_overlap_fraction = 0.75,
                            period_step_octaves=0.125, period_limits=None)        
            #Compute the PSDs
            ppsd.add(tr)
        
            #Save results
            ppsd.save_npz_min(path=outpath)
            logging.debug(f"Worker-{worknumber} -> {sta} processed.")
        except Exception as e:
            logging.debug(f"Worker-{worknumber} -> {sta} ppsd error: {e}")
            continue
    return
        
def get_fargs(csv, jdaylist=[]):
    completeness = pd.read_csv(csv)
    days = completeness.columns[1:]
    fargs = []
    for index, row in completeness.iterrows():
        sta = row.values[0]
        staday = list(days[[bool(s) for s in row.values[1:]]])
        stayear = [int(s.split('.')[0]) for s in staday]
        stajday = [int(s.split('.')[1]) for s in staday]
        for y,j in zip(stayear, stajday):
            fargs.append((sta, '*Z', y, j))
    if not jdaylist:
        return fargs
    else:
        fargs_r = []
        for farg in fargs:
            if farg[3] in jdaylist:
                fargs_r.append(farg)
        return fargs_r
