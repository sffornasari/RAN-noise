import glob
from functools import partial
import os
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning) 
import dask
from dask.distributed import Client
import webbrowser
from utils import otodask
import time

if __name__ == '__main__':
    inpath = '/Archive3/Machine_learning/RAN-noise/sens_only/'
    outpath = '/Archive3/Machine_learning/RAN-noise/sens_only/otoavg/'
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    jdayranges = ['2022.1-95']
    
    files = []
    for jdayrange in jdayranges:
        year, jdays = jdayrange.split('.')
        try:
            jdaymin, jdaymax = jdays.split('-')
        except:
            jdaymin = jdays
            jdaymax = jdays
        for jday in range(int(jdaymin), int(jdaymax)+1):
            files += glob.glob(f'{inpath}/{year}/{int(jday):03d}/*.npz')
            if not os.path.exists(f'{outpath}/{year}/{int(jday):03d}/'):
                os.makedirs(f'{outpath}/{year}/{int(jday):03d}/')
    part_otodask = partial(otodask, outpath=outpath)
    

    client = Client(threads_per_worker=1, n_workers=30)
    
    webbrowser.open('http://localhost:8787/status')
    lazy_results = []
    for f in files:
        lazy_result = dask.delayed(part_otodask)(f)
        lazy_results.append(lazy_result)
    dask.compute(*lazy_results)
    time.sleep(10)
    client.close()
