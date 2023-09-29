import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import glob, os
from progressbar import ProgressBar

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

# Load RAN Model
db = pd.read_csv('../DB/model.csv')

# Load Station Info
df = pd.read_json('../DB/RAN_noise_jsons_2022/yearly_median_all.json')
df.columns = [P.minute*60+P.second+P.microsecond/1000000 for P in df.columns]
df1 = df.sort_index(axis=1)
df = df1.T
periods = df.index.tolist()

ALNM = [ALNM_P(P) for P in db.Period]
AHNM = [AHNM_P(P) for P in db.Period]

mpl.rcParams.update({'font.size': 16})
fig, axs = plt.subplots(6,2,figsize=(20,25),sharex=True,sharey=True)
axs = axs.ravel()
stas = ['ASTI','MRN','GSA','PTL','CHF','CVF','SPD','BLZN','GSM','RSN','SAR','LIC']
usages = ['SL','SL','ACL','ACL','FL','FL','GL','GL','PCL','PCL','OL','OL']
for ax, sta, usage in zip(axs,stas,usages):
# for sta in df.columns:
	ax.plot(periods,df[sta], c='grey', alpha=1)

	ax.plot(db.Period,db.Median, '--r', label='Median')
	ax.plot(db.Period,db.IAHNM,'.--r')
	ax.plot(db.Period,db.IALNM,'.--r',label='IAHNM - IALNM')

	
	ax.semilogx()
	ax.set_xlim(periods[0], 100)
	ax.set_ylim(-140, -80)
	ax.set_title('Station: ' + sta + ' | Land Usage: ' + usage,fontsize=18)


ax.legend(loc='lower right')
# ax.set_ylabel('Power (dB)')
# ax.set_xlabel('Period (s)')
# plt.suptitle('Period (s)', fontsize=14)
fig.add_subplot(111, frameon=False)
# hide tick and tick label of the big axes
plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)
plt.grid(False)
plt.xlabel('Period (s)',fontsize=18)
plt.ylabel('Power (dB)',fontsize=18)
plt.savefig('../Figures/RandomStas.png', dpi=300, bbox_inches='tight')
# plt.show()