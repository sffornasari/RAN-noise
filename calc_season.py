import numpy as np
import pandas as pd
import glob, warnings, os
from datetime import datetime, timedelta
from progressbar import ProgressBar
warnings.filterwarnings('ignore')

def average(lst):
	return sum(lst)/len(lst)


dpc_db = pd.read_csv('../DBs/dpc.csv')

# List Results
syear = '2019'
iyear = int(syear)
days = glob.glob('../DBs/sens_only/' + syear + '/*')
npz = glob.glob(days[0] + '/*')[0]
res = np.load(npz)
keys = list(res.keys())
pn = res[keys[0]]

# 8.00000000e+00 1.00793684e+01
# 1.60000000e+01 2.01587368e+01
# 3.20000000e+01
'''
8s = 28
10s = 29
16s = 31
20= 32
32= 34
'''
s_inxs = [9,13,16,19,22,26]
s_strs = ['0.1','0.25','0.5','1','2','5']
# s_inxs = [28,29,31,32,34]
# s_strs = ['8','10','16','20','32']
# Result List
res_list = []
for period, s_inx in zip(s_strs,s_inxs):
	progress = ProgressBar(max_value=len(days))
	for day_date in progress(days):
		sday = day_date.split('/')[-1]
		day_date_int = int(sday)
		npzs = glob.glob(day_date + '/*')
		for npz in npzs:
			# jday = npz.split('/')[-1].split('_')[-1].split('.')[0]
			# ijday = int(jday)
			fmt = '%Y %j'
			d = datetime.strptime(syear + ' ' + sday, fmt)
			tt = d.timetuple()
			sta = npz.split('/')[-1].split('.')[0]

			res = np.load(npz)
			keys = list(res.keys())
			pn = res[keys[0]]
			st_inx = dpc_db[dpc_db['calibration.sta'] == sta].index.tolist()[0]
			stla = dpc_db['site.lat'][st_inx]
			stlo = dpc_db['site.lon'][st_inx]
			
			# Winter
			winter_vals = []; spring_vals = []; summer_vals = []; autumn_vals = []
			if 1 <= tt.tm_yday <= 59 or 335 <= tt.tm_yday <= 365:
				for trange in keys[1:]:
					winter_vals.append(res[trange][s_inx])
				res_list.append([stla,stlo,sta,float(period),average(winter_vals),'Winter'])
			# Spring
			elif 60 <= tt.tm_yday <= 151:
				for trange in keys[1:]:
					spring_vals.append(res[trange][s_inx])
				res_list.append([stla,stlo,sta,float(period),average(spring_vals),'Spring'])
			# Summer
			elif 152 <= tt.tm_yday <= 243:
				for trange in keys[1:]:
					summer_vals.append(res[trange][s_inx])
				res_list.append([stla,stlo,sta,float(period),average(summer_vals),'Summer'])
			# Autumn
			elif 244 <= tt.tm_yday <= 334:
				for trange in keys[1:]:
					autumn_vals.append(res[trange][s_inx])
				res_list.append([stla,stlo,sta,float(period),average(autumn_vals),'Autumn'])
			else:
				print(tt.tm_yday())
		

res = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','PERIOD','VAL','LABEL'])
res.to_csv('../DBs/season_' + syear + '.csv',index=False)
