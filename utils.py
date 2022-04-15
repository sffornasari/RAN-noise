#Utility functions for PSDs computation
import os
import re
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
from tqdm import tqdm

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
#     for chan in inv._networks[0]._stations[0].channels:
#         chan._code = chan.code[0] + 'N' + chan.code[-1]
        
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
            ext_outpath = f'{outpath}/{year}/{jday:03d}/'
            if not os.path.exists(ext_outpath):
                os.makedirs(ext_outpath)
            ppsd.save_npz_min(path=ext_outpath)
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

#Accelerometric noise models (Cauzzi and Clinton, 2013)
def ALNM():
    Pl = [0.01, 1., 10., 150.,]
    lnm = [-135., -135., -130., -118.25,]
    return Pl, lnm   
def AHNM():
    Ph = [0.01, 0.1, 0.22, 0.32, 0.80, 3.8, 4.6, 6.3, 7.1, 150.,]
    hnm = [-91.5, -91.5, -97.41, -110.5, -120., -98., -96.5, -101., -105., -91.25]
    return Ph, hnm

############################
#One-third-octave averaging#
############################
#Define 1/3 octave bands with nominal frequencies multiple of 1.0
# P is the periods of the psds
# octaveindex is a dictionary with nominal periods as keys ...
# ... and index of the 1/3 octave band as values.
def onethirdoctaves(P):
    N = np.floor(3*np.log2(P[-1])-1/2)
    fu = 1./2**(N/3+1/6)
    ubf = 1/P[0]
    f = 1/P
    Pn = []
    octaveindex = []
    
    while True:
        fl = fu 
        fn = fl*2**(1/6)
        fu = fn*2**(1/6)
        if fu >= ubf:
            break
        Pn.append(1/fn)
        octaveindex.append(np.where((f >= fl) & (f <= fu)))
    return Pn[::-1], octaveindex[::-1]
#Compute the one-third-octave average for a specific PSD       
def octavg(otoi, psd):
    psdavg = [np.nan_to_num(np.mean(psd[idx]), nan=0.0) for idx in otoi]
    return psdavg           
#Compute the one-third-octave average for all PSDs in a given time window
def oto_avg_psd():
    inpath = '/Archive3/Machine_learning/RAN-noise/'
    outpath = '/Archive3/Machine_learning/RAN-noise/otoavg/'
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    jdayranges = ['2020.105']
    
    files = []
    for jdayrange in jdayranges:
        year, jdays = jdayrange.split('.')
        try:
            jdaymin, jdaymax = jdays.split('-')
        except:
            jdaymin = jdays
            jdaymax = jdays
        for jday in range(int(jdaymin), int(jdaymax)+1):
            files += glob.glob(f'{inpath}/{year}/{jday}/*.npz')
    P = np.load(files[0])['P']
    Pn, otoi = onethirdoctaves(P)
    for f in tqdm(files):
        otopsd = {'Pn': Pn}
        sta, cha, year, jday = re.split(r'[/._]', f)[-5:-1]
        npz = np.load(f)
        otopsd.update({h: octavg(otoi=otoi, psd=npz[h]) for h in npz.files[1:]})
        np.savez_compressed(f'{outpath}/{sta}.{cha}_{year}_{jday}', **otopsd)
