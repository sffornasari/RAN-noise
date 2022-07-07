import numpy as np
import pandas as pd
import json
import analysis_utils as autils

otopath = ''
csvpath = ''

P = [0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0]
otofiles = {pi: glob.glob(f'oto_P_ts/oto*{pi:.2e}*npz') for pi in P}

dn = {pi:{} for pi in P}
wdwe = {pi:{} for pi in P}
ws = {pi:{} for pi in P}
for Pk, otok in otofiles.items():
    otos = [np.load(otok[i]) for i in [0,2]]
    moto = autils.merge_otos(otos)
    dn[Pk] = autils.day_night_md(moto)
    ws[Pk] = autils.wint_summ(moto)
    _, __, wdwe[Pk] = autils.wd_we(moto)
    md, s2_5 = autils.yearly_statistics(moto)
    
with open('day_night.json', 'w') as fp:
    json.dump(dn, fp)
with open('wd_we.json', 'w') as fp:
    json.dump(wdwe, fp)
with open('wint_summ.json', 'w') as fp:
    json.dump(ws, fp)
with open('yearly_median.json', 'w') as fp:
    json.dump(md, fp)
with open('yearly_2_5_statistics.json', 'w') as fp:
    json.dump(s2_5, fp)
