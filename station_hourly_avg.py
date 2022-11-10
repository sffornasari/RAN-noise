import numpy as np
import matplotlib.pyplot as plt
import glob, warnings, os
from datetime import datetime, timedelta
from progressbar import ProgressBar
warnings.filterwarnings('ignore')

#Accelerometric noise models (Cauzzi and Clinton, 2013)
def ALNM():
    Pl = [0.01, 1., 10., 150.,]
    lnm = [-135., -135., -130., -118.25,]
    return Pl, lnm   
def AHNM():
    Ph = [0.01, 0.1, 0.22, 0.32, 0.80, 3.8, 4.6, 6.3, 7.1, 150.,]
    hnm = [-91.5, -91.5, -97.41, -110.5, -120., -98., -96.5, -101., -105., -91.25]
    return Ph, hnm

# List Results
year1 = '2019'
year2 = '2022'
station = 'PLTA'
npzs = glob.glob('../DBs/sens_only/' + year1 + '/**/' + station + '*')
npzs += glob.glob('../DBs/sens_only/' + year2 + '/**/' + station + '*')
npzs = list(set(npzs))

pl,lnm = ALNM()
ph,hnm = AHNM()

res = np.load(npzs[0])
org_keys = list(res.keys())
pn = res[org_keys[0]]
# print(pn[2:20])
org_freqs = res[org_keys[0]]
org_keys = org_keys[1:]
middle_times = []
for i,psd in enumerate(org_keys):
	middle_time = datetime.strptime(psd, '%H_%M') + timedelta(minutes=45)
	middle_times.append(middle_time)

progress = ProgressBar(max_value=len(npzs))
vals = np.empty([len(npzs),len(org_keys),len(org_freqs)])
vals[:] = np.nan
for i,npz in progress(enumerate(npzs)):
	res = np.load(npz)
	keys = list(res.keys())
	pn = res[keys[0]]
	for psd in keys[1:]:
		# freqs = np.empty(len(org_keys))
		# freqs[:] = np.nan
		idx = org_keys.index(psd)
		freqs = []
		for freq_val in res[psd]:
			freqs.append(freq_val)
		vals[i,idx,:] = freqs

# high_freq_vals = np.nanmean(vals[:,:,2:20])
# print(high_freq_vals)

fig = plt.figure(figsize=(16, 9),dpi=300)
colors = plt.cm.rainbow(np.linspace(0, 1, len(org_keys)))
for i, hour in enumerate(range(vals.shape[1])):
	avgs = []
	for freq in range(vals.shape[2]):
		avg = np.nanmean(vals[:,hour,freq])
		avgs.append(avg)
	plt.plot(pn,avgs, color=colors[i],label=middle_times[i].strftime('%H %M') + r'$\pm$45m' + ' ' + station)
	# plt.xlim([0,100])
	plt.xlim([0.02008032,10])
	plt.xscale('log')
plt.ylim([-140,-60])

plt.plot(pl,lnm,'k',label='ALNM')
plt.plot(ph,hnm,'k--',label='AHNM')
plt.legend(ncol=6, prop={'size': 6})
if year1 == '2020':
	plt.savefig('../Figures/' + station + '_Hourly_Avg_Covid.png',dpi=300, bbox_inches='tight')
else:
	plt.savefig('../Figures/' + station + '_Hourly_Avg.png',dpi=300, bbox_inches='tight')
# plt.show()	
