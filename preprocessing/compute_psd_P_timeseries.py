import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from functools import partial
import glob
import datetime
import re
import dask
#from dask.distributed import Client
from multiprocessing import Pool
#import webbrowser
import time

def sta_ts(psds, P_ref):
    try:
        ts = []
        t = []
        for psd in psds:
            npz = np.load(psd)
            y, jd = re.split(r'[/._]', psd)[-3:-1]
            t_base = datetime.datetime.strptime(f'{y}{jd}', '%Y%j')
            ind_ref = np.abs(npz['Pn']-P_ref).argmin()
            for h in npz.files[1:]: 
                hpsd = npz[h]
                ts.append(hpsd[ind_ref])
                h, m = re.split(r'[_]', h)
                #t.append(t_base + datetime.timedelta(hours=int(h), minutes=int(m)))
                t.append(int(f'{int(y)}{int(jd):03d}{int(h):02d}{int(m):02d}'))
        return t, ts
    except Exception as e:
        print(e)
    
def mp_sta_ts(P_ref, stas, psds, outpath):
    print(f'{P_ref} starts!')
    if os.path.isfile(f'{outpath}/oto_ts_{P_ref:.2e}_{year}.npz'):
        return
    series = {}
    for sta in stas:
        sta_psds = sorted([psd for psd in psds if f'/{sta}.' in psd])
        if not sta_psds:
            del sta_psds
            continue
        t, ts = sta_ts(sta_psds, P_ref)
        series[sta] = np.array([t, ts])
    np.savez_compressed(f'{outpath}/oto_ts_{P_ref:.2e}_{year}', **series)
    print(f'{P_ref} done!')
    return

def get_times(t):
    t = t.astype(int)
    times = [datetime.datetime.strptime(str(ti), '%Y%j%H%M') for ti in t]
    return times 

if __name__ == '__main__':
    year = 2022

    print(f'Script started at: {time.strftime("%y.%m.%d T%H:%M:%S", time.localtime())}')
    #dask = Client(threads_per_worker=1, n_workers=10, processes=False)
    
    #webbrowser.open('http://localhost:8787/status')
    
    stas = pd.read_csv(f"/home/rt/RAN-noise/wf_dayly_completeness_{year}.csv")['sta'].to_list()
    psds = glob.glob(f'/Archive3/Machine_learning/RAN-noise/full_psd/otoavg/{year}/*/*')
    P_refs = np.load(psds[0])['Pn']
    
    #outpath = f'/Archive3/Machine_learning/RAN-noise/full_psd/oto_P_ts/{year}/'
    outpath = f'full_psd/oto_P_ts/{year}/'
    if not os.path.exists(outpath):
        os.makedirs(outpath)
        
    partial_ts = partial(mp_sta_ts, stas=stas, psds=psds, outpath=outpath)
    
    
    #lazy_results = []
    #for P_ref in P_refs:
        #partial_ts(P_ref)
    #    lazy_result = dask.delayed(partial_ts)(P_ref)
    #     lazy_results.append(lazy_result)
    #dask.compute(*lazy_results)
    
    with Pool(30) as p:
        p.map(partial_ts, P_refs)
    
    time.sleep(15)
    #client.close()
