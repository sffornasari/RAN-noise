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
	df = df[df['mag'] <= 4]

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
	mags = np.arange(1,5)
	for mag in mags:
		df_plot = df_text[df_text['mag'] == mag]
		ax.text(df_plot['T'], df_plot['dB']+4, 
				"M{0}".format(mag), va='center', ha='center', 
				color=gridcolor)
	df_text = df[df['mag'] == 4]
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

# Load EQ recorded statios
db_eq = pd.read_csv('../DB/495323.csv')
db_eq = db_eq.sort_values(by=['dist (km)'])
dist_min = db_eq['dist (km)'].min()
dist_max = db_eq['dist (km)'].max()

ALNM = [ALNM_P(P) for P in db.Period]
AHNM = [AHNM_P(P) for P in db.Period]

mpl.rcParams.update({'font.size': 16})

fig, ax = plt.subplots(figsize=(10,6))

from matplotlib import cm

for sta in df.columns:
	if sta in db_eq.Sta.tolist():
		if sta == 'TLN':
			ax.plot(periods,df[sta], c=cm.copper(db_eq[db_eq.Sta==sta].iloc[0]['dist (km)']/dist_max),linewidth=3, alpha=1,zorder=5)
		else:
			ax.plot(periods,df[sta], c=cm.copper(db_eq[db_eq.Sta==sta].iloc[0]['dist (km)']/dist_max), alpha=0.5)

cmap = plt.get_cmap('copper')
norm = mpl.colors.Normalize(vmin=dist_min,vmax=dist_max)
fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, label=r'R$_{epi}$ (km)')
# ax.colorbar(vmin=dist_min/dist_max,vmax=1)
ax.plot(db.Period,db.Median, '--r', label='Median')
ax.plot(db.Period,db.IAHNM,'.--r')
ax.plot(db.Period,db.IALNM,'.--r',label='IAHNM - IALNM')

# Plot Brune corner frequency grid
plotBrune(ax)

# from mpl_toolkits.axes_grid1.inset_locator import inset_axes
# axins = inset_axes(ax, width="30%", height="30%",
# 					bbox_to_anchor=(-0.025,-0.43,1,1), bbox_transform=ax.transAxes)
# from obspy import read

# st = read('../DB/495323_sac/*TLN*',format='SAC')
# st.detrend('linear')
# st.taper(0.05,'hann')
# st.filter('bandpass',freqmin=1.6,freqmax=42.5)
# fig2, axs = plt.subplots(3,1,sharex=True,sharey=True)
# axs = np.ravel(axs)
# for i, sm_ax in enumerate(axs):
# 	axins.plot(st[i].times("matplotlib"), st[i].data*10**-9, "k-")
# 	axins.set_xlim(st[i].times("matplotlib")[0],st[i].times("matplotlib")[-1])
# 	axins.xaxis_date()
# fig2.autofmt_xdate()
# # st.plot(ax=axins)
# axins.set_xticks([])
# axins.set_yticks([])


ax.set_ylabel('Power (dB)')
ax.set_xlabel('Period (s)')
ax.semilogx()
ax.set_xlim(periods[0], 100)
ax.set_ylim(-200, -50)

ax.legend(loc='lower right')
fig.savefig('../Figures/495323.png', dpi=300, bbox_inches='tight')
# plt.show()