import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn import metrics

def ALNM_P(P):
    Pl = [0.01, 1., 10., 150.,]
    lnm = [-135., -135., -130., -118.25,]
    if Pl[0]<=P<=Pl[-1]:
        lnm_P = np.interp(P, Pl, lnm)
        return lnm_P
    else:
        print(f'P={P} out of ALNM range.')
        return np.nan
def AHNM_P(P):
    Ph = [0.01, 0.1, 0.22, 0.32, 0.80, 3.8, 4.6, 6.3, 7.1, 150.,]
    hnm = [-91.5, -91.5, -97.41, -110.5, -120., -98., -96.5, -101., -105., -91.25]
    if Ph[0]<=P<=Ph[-1]:    
        hnm_P = np.interp(P, Ph, hnm)
        return hnm_P
    else:
        print(f'P={P} out of ALNM range.')
        return np.nan

df = pd.read_json('yearly_median_all.json')
df.columns = [P.minute*60+P.second+P.microsecond/1000000 for P in df1.columns]
df = df1.sort_index(axis=1)
  
df = pd.read_json('yearly_median_all.json')
df.columns = [P.minute*60+P.second+P.microsecond/1000000 for P in df1.columns]
df = df1.sort_index(axis=1)

netmedian = []
for c in df1.columns:
  netmedian.append(df1[c].median(axis=0))
  
a = df.to_numpy().ravel()
PP = list(range(50))*len(df)
P = list(range(50))

ALNM = [ALNM_P(P) for P in df1.columns]
AHNM = [AHNM_P(P) for P in df1.columns]

mpl.rcParams.update({'font.size': 16})

fig, ax = plt.subplots(figsize=(10,6))

h = ax.hist2d(PP, a, bins=(40, 61*2),  range=[[0, 39],[-140,-80]], cmap='viridis', norm=mpl.colors.Normalize(vmin=0, vmax=75))
ax.plot(P, netmedian, '--w', label='Network median')
ax.plot(P, ALNM, 'w')
ax.plot(P, AHNM, 'w', label='NLNM|NHNM')

ax.set_ylabel('Power (dB)')
ax.set_xlabel('Period (s)')

ax.set_xticks([0,9,19,29,39])
ax.set_xticklabels([0.01,0.1,1,10,100], minor=False)
cbar = fig.colorbar(h[3], ax=ax, ticks=[0, 25, 50, 75], label='Probability')
cbar.ax.set_yticklabels(['0%', '5%', '10%', '15%'])
ax.legend(loc='upper right')
plt.savefig('netmedian.png', dpi=300)
plt.show()
