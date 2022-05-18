import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import glob, warnings, os
from datetime import datetime, timedelta
from progressbar import ProgressBar
warnings.filterwarnings('ignore')

def average(lst):
	return sum(lst)/len(lst)

dpc_db = pd.read_csv('../DBs/dpc.csv')

# List Results
syear = '2022'
iyear = int(syear)
days = glob.glob('../DBs/sens_only/' + syear + '/*')

'''
1s = 19
2s = 22
5s = 26
0.5= 16
0.25= 13
0.1= 9
'''
s_inxs = [9,13,16,19,22,26]
s_strs = ['0.1','0.25','0.5','1','2','5']
# Result List
res_list = []
for period, s_inx in zip(s_strs,s_inxs):
	progress = ProgressBar(max_value=len(days))
	for day_date in progress(days):
		sday = day_date.split('/')[-1]
		day_date_int = int(sday)
		npzs = glob.glob(day_date + '/*')
		for npz in npzs:
			sta = npz.split('/')[-1].split('.')[0]
			# year,jday = npz.split('/')[-1].split('.')[1].split('_')[1:]
			# date_time_obj = datetime.strptime(year + '_' + jday, '%Y_%j')
			# date = date_time_obj.strftime('%A %d %b %Y')
			res = np.load(npz)
			keys = list(res.keys())
			pn = res[keys[0]]

			st_inx = dpc_db[dpc_db['calibration.sta'] == sta].index.tolist()[0]
			stla = dpc_db['site.lat'][st_inx]
			stlo = dpc_db['site.lon'][st_inx]
			res_days = keys[9:-5]
			nights = keys[1:8] + keys[-4:]
			days_vals = [];
			if len(res_days) > 0:
				for res_day in res_days:
					days_vals.append(res[res_day][s_inx])
				res_list.append([stla,stlo,sta,float(period),average(days_vals),'Day'])
			# else:
			# 	res_list.append([stla,stlo,sta,float(period),np.NAN,'Day'])
			nights_vals = [];
			if len(nights) > 0:
				for night in nights:
					nights_vals.append(res[night][s_inx])
				res_list.append([stla,stlo,sta,float(period),average(nights_vals),'Night'])
			# else:
			# 	res_list.append([stla,stlo,sta,float(period),np.NAN,'Night'])
		


res = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','PERIOD','VAL','LABEL'])
res.to_csv('../DBs/day_night_' + syear + '.csv',index=False)