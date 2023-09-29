import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import glob, os
from progressbar import ProgressBar

def plotBrune(ax):
	'''Plot Brune corner frequencies for mag/dist ranges of interest
	   (see esupp for details on calculation)'''
	# Read file containing list of corner frequencies
	dirname = os.path.dirname(__file__)
	brunecsv = os.path.join(dirname,'../DB/brune-all.csv')
	df = pd.read_csv(brunecsv, names=['delta', 'mag', 'T', 'dB'], 
					 skiprows=1, sep=',')
	df = df[df['mag'] <= 6]

	# Plot grid of corner frequencies:
	# Draw lines connecting all magnitudes at a given distance,
	# then all distances at a given magnitude 
	gridcolor='#1f77b4' # darker blue
	linestyle={'color' : gridcolor,
			   'mfc' : gridcolor,
			   'linewidth' : 1,
			   'linestyle' : '--'}
	deltas = pd.unique(df['delta'])
	for delta in deltas:
		df_subset = df[df['delta'] == delta]
		if delta == 1:
			label=r'Brune f$_c$'
		else:
			label=''
		ax.plot(df_subset['T'], df_subset['dB'], marker='.', 
				**linestyle, label=label)
	mags = pd.unique(df['mag'])
	for mag in mags:
		df_subset = df[df['mag'] == mag]
		ax.plot(df_subset['T'], df_subset['dB'], marker='None', 
				**linestyle, label='')

	# Plot labels on grid for magnitudes and distances
	df_text = df[df['delta'] == 0.01]
	mags = np.arange(1,7)
	for mag in mags:
		df_plot = df_text[df_text['mag'] == mag]
		ax.text(df_plot['T'], df_plot['dB']+4, 
				"M{0}".format(mag), va='center', ha='center', 
				color=gridcolor)
	df_text = df[df['mag'] == 6]
	for delta in deltas:
		df_plot = df_text[df_text['delta'] == delta]
		ax.text(df_plot['T']+0.02, df_plot['dB']+2.5, 
				"{0:0d} km".format(int(delta*100)), va='center', 
				rotation=30, color=gridcolor)

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

fig, ax = plt.subplots(figsize=(10,6))


for sta in df.columns:
	ax.plot(periods,df[sta], c='grey', alpha=0.3)

ax.plot(db.Period,db.Median, '--r', label='Median')
ax.plot(db.Period,db.IAHNM,'.--r')
ax.plot(db.Period,db.IALNM,'.--r',label='IAHNM - IALNM')

ax.set_ylabel('Power (dB)')
ax.set_xlabel('Period (s)')
ax.semilogx()
ax.set_xlim(periods[0], 100)
ax.set_ylim(-180, -20)
# ax.set_ylim(-140, -80)

# Plot Brune corner frequency grid
plotBrune(ax)

ax.legend(loc='lower right')
plt.savefig('../Figures/stationwise.png', dpi=300, bbox_inches='tight')
# plt.show()