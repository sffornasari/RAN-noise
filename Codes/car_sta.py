import numpy as np
from obspy import read
import pandas as pd
import matplotlib.pyplot as plt
import glob, warnings, os
from datetime import datetime, timedelta
from progressbar import ProgressBar
from scipy.interpolate import interp1d
warnings.filterwarnings('ignore')

# List Results
year1 = '2019'
year2 = '2022'
station = 'PLTA'
npzs = glob.glob('../DBs/sens_only/' + year1 + '/**/' + station + '*')
npzs += glob.glob('../DBs/sens_only/' + year2 + '/**/' + station + '*')
npzs = list(set(npzs))

# Lower & Higher Thresholds
x_low = [0.01,0.1,10,150]
y_low = [-135,-135,-130,-118.25]
x_high = [0.01,0.1,0.22,0.32,0.80,3.8,4.6,6.3,7.1,150]
y_high = [-91.5,-91.5,-97.41,-110.5,-120,-98,-96.5,-101,-105,-91.25]
f1_low = interp1d(x_low, y_low, kind='linear')
f1_high = interp1d(x_high, y_high, kind='linear')
periods = np.linspace(0.01,10,num=1000)
lnm = [f1_low(period).tolist() for period in periods]
hnm = [f1_high(period).tolist() for period in periods]

res = np.load(npzs[0])
org_keys = list(res.keys())
pn = res[org_keys[0]]
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
		idx = org_keys.index(psd)
		freqs = []
		for freq_val in res[psd]:
			freqs.append(freq_val)
		vals[i,idx,:] = freqs

fig,axs = plt.subplots(2,1, figsize=(16,14), facecolor='w', sharex=True, edgecolor='k')#, , gridspec_kw = {'wspace':0, 'hspace':0.1}
axs = axs.ravel()

colors = plt.cm.rainbow(np.linspace(0, 1, len(org_keys)))
for i, hour in enumerate(range(vals.shape[1])):
	avgs = []
	for freq in range(vals.shape[2]):
		avg = np.nanmean(vals[:,hour,freq])
		avgs.append(avg)
	axs[0].plot(pn,avgs, color=colors[i],label=middle_times[i].strftime('%H %M') + r'$\pm$45m' + ' ' + station)
	axs[0].set_xlim([0.02008032,10])
	axs[0].set_xscale('log')
axs[0].set_ylim([-140,-60])

axs[0].plot(periods,lnm,'k',label='ALNM')
axs[0].plot(periods,hnm,'k--',label='AHNM')
axs[0].legend(ncol=6, prop={'size': 6})

# FFT
def calc_fft(data):
	samp = 100 
	Fdat = np.fft.rfft(data)
	freq = np.fft.rfftfreq(data.shape[0], d=1./samp)
	return 2.0/samp * np.abs(Fdat), freq

# # Signal Length
dlen_s = '10'
dlen = 10 * 100

# Load DB
station = 'PLTA'
all_files = glob.glob('../DBs/Car_Detection/Manual_Picks/' + station + '*.csv')

li = []

car_output = []; car_output_fft = [];

count = 0
for filename in all_files[:]:
	df = pd.read_csv(filename, index_col=None, header=0)
	date = filename.split('/')[-1].split('.')[0].split('_')[-1]
	sta = filename.split('/')[-1].split('.')[0].split('_')[0]
	df['dif'] = df['End'] - df['Start']

	if dlen == 500:
		df = df[(df.dif > 1) & (df.dif <= 20)]
	elif dlen == 1000:
		df = df[(df.dif > 5) & (df.dif <= 2*int(dlen_s))]
	elif dlen == 2000:
		df = df[(df.dif > 5) & (df.dif <= 2*int(dlen_s))]

	progress = ProgressBar(max_value=len(df))

	st = read('../../../Car_Detection/Data_Sta/' + sta + '/' + date + '.00.' + sta + '.HNZ')
	st.detrend('simple')
	st.filter('bandpass',freqmin=0.5,freqmax=50)
	st.resample(100)
	for tr in st:
		tr.data = tr.data * 10**-9

	for start, end in progress(zip(df.Start, df.End)):
		st_copy = st.copy()
		output = []; output_fft = [];
		max_amp = []
		flag = False
		for tr in st_copy:
			start_val = int(start*st_copy[0].stats.sampling_rate)
			end_val = int(end*st_copy[0].stats.sampling_rate)
			data = tr.data[start_val:end_val]
			zero_len = dlen - len(data)
			if zero_len > 0:
				zero_trace = np.zeros(int(zero_len))
				data = np.concatenate((data, zero_trace))
			else:
				data = data[:dlen]
			data = np.where(np.isnan(data), 0, data)
			if max(abs(data)) == 0:
				flag = True
			freq, freq_to_use = calc_fft(data)
			output_fft.append(freq[:500])
			output.append(data)
		if flag == False:
			output = np.array(output)
			output_fft = np.array(output_fft)
			if np.any(np.isnan(output)):
				output = np.where(np.isnan(output), 0, output)
			car_output.append(output)
			car_output_fft.append(output_fft)
			count += 1

car_fft = np.array(car_output_fft)

car_average_vertical = []
for i in range(car_fft.shape[-1]):
	z = car_fft[:,0,i]
	av_z = np.mean(z)
	car_average_vertical.append(av_z)

freq_to_use = freq_to_use[:500]
freq_to_use = np.reciprocal(freq_to_use)

axs[1].plot(freq_to_use,car_average_vertical,c='b',linestyle='-',linewidth=1)
axs[1].set_xscale('log')
axs[1].set_xlim([0.02008032,10])
axs[1].set_yticks([])
axs[1].set_xlabel('Period (s)')

plt.savefig('../Figures/Figure15.png', bbox_inches='tight')
