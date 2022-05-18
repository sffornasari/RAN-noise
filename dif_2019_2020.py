import os, glob
import numpy as np
import pandas as pd
from progressbar import ProgressBar

def average(lst):
	return sum(lst)/len(lst)


year1 = '2019'
year2 = '2022'

# 2019 Dataset
npz2019 = glob.glob('../DBs/sens_only/' + year1 + '/**/*.npz', recursive=True)
stas_2019 = []

for i in npz2019:
	sta = i.split('/')[-1].split('.')[0]
	if sta not in stas_2019:
		stas_2019.append(sta)

# 2020 Dataset
npz2020 = glob.glob('../DBs/sens_only/' + year2 + '/**/*.npz', recursive=True)
stas_2020 = []

for i in npz2020:
	sta = i.split('/')[-1].split('.')[0]
	if sta not in stas_2020:
		stas_2020.append(sta)


# Emtpy Database
res = np.load(npz2020[0])
keys = list(res.keys())
# Frequencies
pn = res[keys[0]][:-10]
columns = np.array(['Station'])
for i in pn:
	columns = np.append(columns,"{:.3f}".format(round(i,3)).zfill(7))
columns = np.array(columns)
columns = np.append(columns,'Average')
common_stas = np.intersect1d(stas_2019, stas_2020)

progress = ProgressBar(max_value=len(common_stas))
res_list = np.array([])
for sta in progress(common_stas):
	try:
		vals2019 = []; vals2020 = []
		# 2019 data:
		data2019 = glob.glob('../DBs/sens_only/' + year1 + '/**/' + sta + '*.npz', recursive=True)
		# 2020 data:
		data2020 = glob.glob('../DBs/sens_only/' + year2 + '/**/' + sta + '*.npz', recursive=True)

		for npz in data2019:
			res = np.load(npz)
			keys = list(res.keys())
			# Frequencies
			pn = res[keys[0]]
			# Hours
			hours = keys[1:]
			for i,psd in enumerate(keys[1:]):
				vals2019.append(res[psd][:-10])
		
		for npz in data2020:
			res = np.load(npz)
			keys = list(res.keys())
			# Frequencies
			pn = res[keys[0]]
			# Hours
			hours = keys[1:]
			for i,psd in enumerate(keys[1:]):
				vals2020.append(res[psd][:-10])
		

		vals2019 = np.array(vals2019)
		vals2020 = np.array(vals2020)
		# Averages of Each Period
		avg2019 = np.average(vals2019, axis=0)
		avg2020 = np.average(vals2020, axis=0)
		# Average of all periods
		total_avg2019 = np.average(vals2019, axis=None)
		total_avg2020 = np.average(vals2020, axis=None)
		# Merge in a single array
		vals2019 = np.append(avg2019,total_avg2019)
		vals2020 = np.append(avg2020,total_avg2020)
		# Calculate Dif
		dif = vals2019 - vals2020
		dif = dif.tolist()
		dif.insert(0,sta)
		# res_list = np.vstack([res_list, dif])
		res_list = np.append(res_list,dif)
	except:
		res_list = np.append(res_list,np.zeros(len(pn)))


res_list = res_list.reshape(len(common_stas),len(columns))
db = pd.DataFrame(res_list,columns = columns)
db.to_csv('../DBs/Dif_Periodwise_' + year1 + year2 + '.csv',index=False)
	
