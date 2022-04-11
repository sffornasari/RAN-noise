#Dummy exemple
from utils import get_fargs, onestation_psd
import warnings, os
warnings.filterwarnings("ignore", message="'b'<Dip ")
warnings.filterwarnings("ignore", message="'b'<Azimuth ")
import logging
from functools import partial
import dask
from dask.distributed import Client, progress
import webbrowser

if __name__ == '__main__':
    #logging.basicConfig(level = logging.DEBUG)
    client = Client(threads_per_worker=1, n_workers=32)
    
    webbrowser.open('http://localhost:8787/status')
    
    #Compute daily PSDs
    jdaymin = 69
    jdaymax = 104
    fargs = get_fargs('wf_dayly_completeness.csv', list(range(jdaymin, jdaymax+1)))
    wfpath = '/Archive4/RANdb_2/from_DPC/'
    invpath = '/home/rt/RAN-noise/StationXML/'
    outpath = '/home/rt/RAN-noise/test_out/'
    if not os.path.exists(outpath):
        os.makedirs(outpath)
        
    partial_onestation_psd = partial(onestation_psd, wfpath=wfpath, invpath=invpath, outpath=outpath)
    
    lazy_results = []
    for args in fargs:
        lazy_result = dask.delayed(partial_onestation_psd)(*args)
        lazy_results.append(lazy_result)
    dask.compute(*lazy_results)
