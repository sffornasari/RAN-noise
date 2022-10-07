"""
This compute all the outputs used in the paper.
The file selection is an ad hoc solution for our data: the lines with otos = ... should be modified consequently.
"""

import os
import pandas as pd
import numpy as np
import glob
import datetime
import analysis_utils as autils
import json
import tqdm

# Paths
otopath = ''
outpath = ''
if not os.path.exists(outpath):
   os.makedirs(outpath)

# Define periods of interest
P = [0.0625, 0.0992, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 5.04, 8.0, 16.0, 32.0, 64.0, 80.6]

# Find .npz files
otofiles = {pi: glob.glob(f'{otopath}/*/oto*{pi:.2e}*npz') for pi in P}

# Compute differences and statistics
## YEARS 2019 & 2022
dn = {pi:{} for pi in P}
wdwe = {pi:{} for pi in P}
ws = {pi:{} for pi in P}
md = {pi:{} for pi in P}
wdwe = {pi:{} for pi in P}
s2_5 = {pi:{} for pi in P}
for Pk, otok in otofiles.items():
    otos = [np.load(otok[i]) for i in [0,2]]
    moto = autils.merge_otos(otos)
    dn[Pk] = autils.day_night_md(moto)
    ws[Pk] = autils.sum_win(moto)
    _, __, wdwe[Pk] = autils.wd_we_md(moto)
    md[Pk], s2_5[Pk] = autils.yearly_statistics(moto)
with open(f'{outpath}/day_night_ext.json', 'w') as fp:
    json.dump(dn, fp)
with open(f'{outpath}/wd_we_ext.json', 'w') as fp:
    json.dump(wdwe, fp)
with open(f'{outpath}/wint_summ_ext.json', 'w') as fp:
    json.dump(ws, fp)
with open(f'{outpath}/yearly_median_ext.json', 'w') as fp:
    json.dump(md, fp)
with open(f'{outpath}/yearly_2_5_statistics_ext.json', 'w') as fp:
    json.dump(s2_5, fp)
## YEAR 2020 - COVID LOCKDOWN
dn = {pi:{} for pi in P}
wdwe = {pi:{} for pi in P}
#ws = {pi:{} for pi in P}
md = {pi:{} for pi in P}
wdwe = {pi:{} for pi in P}
s2_5 = {pi:{} for pi in P}
for Pk, otok in otofiles.items():
    # otos = [np.load(otok[i]) for i in [1]]
    # moto = autils.merge_otos(otos)
    moto = np.load(otok[0])
    dn[Pk] = autils.day_night_md(moto)
    #ws[Pk] = autils.sum_win(moto)
    _, __, wdwe[Pk] = autils.wd_we_md(moto)
    md[Pk], s2_5[Pk] = autils.yearly_statistics(moto)
with open(f'{outpath}/day_night_ext_covid.json', 'w') as fp:
    json.dump(dn, fp)
with open(f'{outpath}/wd_we_ext_covid.json', 'w') as fp:
    json.dump(wdwe, fp)
#with open(f'{outpath}/wint_summ_ext_covid.json', 'w') as fp:
#    json.dump(ws, fp)
with open(f'{outpath}/yearly_median_ext_covid.json', 'w') as fp:
    json.dump(md, fp)
with open(f'{outpath}/yearly_2_5_statistics_ext_covid.json', 'w') as fp:
    json.dump(s2_5, fp)
	
# Compute COVID-NONCOVID differences
cases = ['day_night_ext',
         'wd_we_ext',
         'yearly_2_5_statistics_ext',
         'yearly_median_ext',
         ]
for fname in cases:
    covid_diff = {}
    with open(f'{outpath}/{fname}.json', 'r') as fp:
        jdata = json.load(fp)
    with open(f'{outpath}/{fname}_covid.json', 'r') as fp:
        jdata_c = json.load(fp)
    for k in jdata.keys():
        covid_diff[float(k)] = {}
        for sta in jdata[k].keys():
            if sta in jdata_c[k]:
                covid_diff[float(k)][sta] = jdata[k][sta]-jdata_c[k][sta]
    with open(f'{outpath}/{fname}_covid_diff.json', 'w') as fp:
        json.dump(covid_diff, fp)
		
# Compute day and night values
## YEARS 2019 & 2022
dn = {pi:{} for pi in P}
mds = {pi:{} for pi in P}
mns = {pi:{} for pi in P}
for Pk, otok in otofiles.items():
    otos = [np.load(otok[i]) for i in [0,2]]
    moto = autils.merge_otos(otos)
    mds[Pk], mns[Pk], __ = autils.day_night_md_mod(moto)
with open(f'{outpath}/day_ext.json', 'w') as fp:
    json.dump(mds, fp)
with open(f'{outpath}/night_ext.json', 'w') as fp:
    json.dump(mns, fp)	
## YEAR 2020 - COVID LOCKDOWN
dn = {pi:{} for pi in P}
mds = {pi:{} for pi in P}
mns = {pi:{} for pi in P}
for Pk, otok in otofiles.items():
    #otos = [np.load(otok[i]) for i in [1]]
    #moto = autils.merge_otos(otos)
    moto = np.load(otok[0])
    mds[Pk], mns[Pk], __ = autils.day_night_md_mod(moto)
with open(f'{outpath}/day_ext_covid.json', 'w') as fp:
    json.dump(mds, fp)
with open(f'{outpath}/night_ext_covid.json', 'w') as fp:
    json.dump(mns, fp)
	
# Compute weekday and weekend values
## YEARS 2019 & 2022
wds = {pi:{} for pi in P}
wes = {pi:{} for pi in P}
for Pk, otok in otofiles.items():
    otos = [np.load(otok[i]) for i in [0,2]]
    moto = autils.merge_otos(otos)
    wds[Pk], wes[Pk], __ = autils.wd_we_md(moto)
with open(f'{outpath}/wd_ext.json', 'w') as fp:
    json.dump(wds, fp)
with open(f'{outpath}/we_ext.json', 'w') as fp:
    json.dump(wes, fp)
## YEAR 2020 - COVID LOCKDOWN
wds = {pi:{} for pi in P}
wes = {pi:{} for pi in P}
for Pk, otok in otofiles.items():
    otos = [np.load(otok[i]) for i in [1]]
    moto = autils.merge_otos(otos)
    wds[Pk], wes[Pk], __ = autils.wd_we_md(moto)
with open(f'{outpath}/wd_ext_covid.json', 'w') as fp:
    json.dump(wds, fp)
with open(f'{outpath}/we_ext_covid.json', 'w') as fp:
    json.dump(wes, fp)

	
# Compute statistics for all periods
P_all = sorted([float(P.split('_')[-2]) for P in glob.glob(f'{otopath}/*/oto*.npz')])
otofiles = {pi: glob.glob(f'{otopath}/*/oto*{pi:.2e}*npz') for pi in P_all}
#YEARS 2019 & 2022
md = {pi:{} for pi in P_all}
s2_5 = {pi:{} for pi in P_all}
for Pk, otok in otofiles.items():
    otos = [np.load(otok[i]) for i in [0,2]]
    moto = autils.merge_otos(otos)
    md[Pk], s2_5[Pk] = autils.yearly_statistics(moto)
with open(f'{outpath}/yearly_median_all.json', 'w') as fp:
    json.dump(md, fp)
with open(f'{outpath}/yearly_2_5_statistics_all.json', 'w') as fp:
    json.dump(s2_5, fp)
