import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob, os, json, mpld3


def plotBrune(ax):
	'''Plot Brune corner frequencies for mag/dist ranges of interest
	   (see esupp for details on calculation)'''
	# Read file containing list of corner frequencies
	dirname = os.path.dirname(__file__)
	brunecsv = '../../DBs/brune-all.csv'
	df = pd.read_csv(brunecsv, names=['delta', 'mag', 'T', 'dB'], 
					 skiprows=1, sep=',')
	df = df[(df['mag'] >= 1)&(df['mag'] <= 6)]

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
			label=r'Brune 1970 f$_c$'
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

# Opening JSON file
f = open('../../DBs/JSON_Final/yearly_median_all.json')
# returns JSON object as 
# a dictionary
data = json.load(f)

periods = [i for i in data.keys()][:-9]
periods_float = [float(i) for i in data.keys()][:-9]

stnames = []; vals = []
for per_idx, period in enumerate(periods):
	# print(period)
	for sta in data[period]:
		val = data[period][sta]
		vals.append(val)
		stnames.append(sta)

db_all = pd.DataFrame({'Station':stnames,'Vals':vals})

medians = [];
for sta in db_all.Station.unique():
	medians.append(db_all[db_all.Station == sta].Vals.median())

db_median = pd.DataFrame({'Station':db_all.Station.unique(),'Median':medians})

top10 = db_median.sort_values(by='Median', ascending=False)[:10].Station.tolist()

fig, ax = plt.subplots(figsize=(16,9))
for sta in top10:
	vals = []; topperiods = []
	ALNMs = []; AHNMs = []
	for period in periods:
		topperiods.append(float(period))
		val = data[period][sta]
		vals.append(val)
		ALNMs.append(ALNM_P(float(period)))
		AHNMs.append(AHNM_P(float(period)))
	ax.plot(topperiods,vals,label='{} | Median: {}'.format(sta,round(db_median[db_median.Station==sta].Median.tolist()[0]),1))

plotBrune(ax)
ax.plot(topperiods,ALNMs,c='k',label='ALNM')
ax.plot(topperiods,AHNMs,c='k',label='AHNM')
ax.set_ylabel('Power (dB)')
ax.set_xlabel('Period (s)')
ax.semilogx()
ax.set_xlim(0.01, 120)
ax.set_ylim(-180, 0)
ax.legend(ncol=5,loc='lower right')
# plt.show()
plt.savefig('../../Figures/top10.png',dpi=300, bbox_inches='tight')
mpld3.save_html(fig,'../../Figures/top10.html')
	