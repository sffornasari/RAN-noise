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
s_inxs = [31,34,38]
s_strs = ['16','32','80.6']
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
			sta = npz.split('/')[-1].split('.')[0]

			res = np.load(npz)
			keys = list(res.keys())
			pn = res[keys[0]]
			st_inx = dpc_db[dpc_db['calibration.sta'] == sta].index.tolist()[0]
			stla = dpc_db['site.lat'][st_inx]
			stlo = dpc_db['site.lon'][st_inx]
			
			# Weekend
			weekend_vals = []; weekday_vals = []; 
			if d.weekday() > 4:
				for trange in keys[1:]:
					weekend_vals.append(res[trange][s_inx])
				res_list.append([stla,stlo,sta,float(period),average(weekend_vals),'Weekend'])
			# Weekday
			else:
				for trange in keys[1:]:
					weekday_vals.append(res[trange][s_inx])
				res_list.append([stla,stlo,sta,float(period),average(weekday_vals),'Weekday'])
		

res = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','PERIOD','VAL','LABEL'])
res.to_csv('../DBs/longperiod_' + syear + '.csv',index=False)
# Drop Outliears
# res = res[~res['STNAME'].isin(['CES','SLD'])]

# weekday = res[res.LABEL == 'Weekday']
# weekday = weekday.groupby(['STNAME','STLA','STLO'], as_index=False, sort=False)['VAL'].mean()
# weekend = res[res.LABEL == 'Weekend']
# weekend = weekend.groupby(['STNAME','STLA','STLO'], as_index=False, sort=False)['VAL'].mean()

