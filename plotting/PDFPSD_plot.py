#%%
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt

from obspy.signal.spectral_estimation import get_nlnm
from obspy.signal.spectral_estimation import get_nhnm

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

# Peterson 1993
peter_low_T, peter_low_PSD = get_nlnm()
peter_high_T, peter_high_PSD = get_nhnm()

# D'Alessandro
dales_T = 1/np.array([0.022,0.032,0.046,0.064,0.083,0.1,0.167,0.2,0.233,0.417,0.806,1.25,2.5,5.882,10,12,18,24,30])
dales_low_PSD = np.array([-173,-174,-170.6,-164,-165,-162.6,-146.8,-142.6,-141,-147.2,-152.8,-155,-156.2,-155,-152,-150,-147.4,-143.1,-141.5])
dales_high_PSD = np.array([-117,-118,-118,-118.5,-120.5,-118.6,-107.4,-104.6,-102.6,-101,-99,-100.8,-98.2,-93.3,-86.8,-85.1,-85.2,-87,-84.5])

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


df = pd.read_json('../DB/RAN_noise_jsons_2022/yearly_median_all.json')
df.columns = [P.minute*60+P.second+P.microsecond/1000000 for P in df.columns]
df1 = df.sort_index(axis=1)

netmedian = []
# 5% and 95% percentiles
p5s= []
p95s = []
for c in df1.columns:
	netmedian.append(df1[c].median(axis=0))
	p5s.append(np.percentile(df1[c],5))
	p95s.append(np.percentile(df1[c],95))

# Save Results
db_model = pd.DataFrame({'Period':df1.columns,'Median':netmedian,'IALNM':p5s,'IAHNM':p95s})
db_model.to_csv('../DB/italian_model.csv',index=False)

a = df.to_numpy().ravel()

P = list(df1.columns)
PP = P*len(df)

ALNM = [ALNM_P(Pi) for Pi in P]
AHNM = [AHNM_P(Pi) for Pi in P]

NHNM = np.interp(P, peter_high_T[::-1], peter_high_PSD[::-1])

mpl.rcParams.update({'font.size': 16})

fig, ax = plt.subplots(figsize=(20,12))


H, xedges, yedges = np.histogram2d(PP, a, bins=(P, np.arange(-140, -79.5, 0.5)))
im = ax.pcolormesh(xedges, yedges, H.T, cmap='viridis')
line0 = ax.plot(P, netmedian, linestyle='dashed',color='w', label='Network median',linewidth=5)
ax.plot(P,p5s,linestyle = '-',color='w',linewidth=3)
line1 = ax.plot(P,p95s,linestyle = '-',color='w',label='IAHNM',linewidth=3)

#Cauzzi
ax.plot(P, ALNM, 'C3',linewidth=3)
line2 = ax.plot(P, AHNM, 'C3', label='ALNM|AHNM',linewidth=3)
# Peterson
ax.plot(peter_low_T, peter_low_PSD, 'C1',linewidth=3)
line3 = ax.plot(P, NHNM, 'C1', label='NHNM',linewidth=3)
# D'Alessandro
ax.plot(dales_T, dales_low_PSD, 'C6',linewidth=3)
line4 = ax.plot(dales_T, dales_high_PSD, 'C6', label=r'H$_{INM}$',linewidth=3)

ax.set_xscale('log')
ax.set_xlim(0.01+0.005,100)
ax.set_xticks([])
ax.set_xticks([], minor=True)

ax.set_xlabel('Period (s)')
ax.set_ylabel(r'Power (dB relative to 1 (m/s$^{2}$)$^{2}$/Hz)', rotation=90, size=18)

cbar = fig.colorbar(im, ax=ax, label='Probability')
# cbar.ax.set_yticklabels(['0%', '5%', '10%', '15%'])

# added these three lines
lns = line0+line1+line2+line3+line4
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc='upper right')

ax.set_xscale('log')
ax.set_xlim([0.015,100])
ax.set_ylim([-140,-80])

plt.savefig('../Figures/netmedian.png', dpi=300, bbox_inches='tight')
