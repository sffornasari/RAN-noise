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

def minmax(data1,data2):
	vmin = min([min(data1),min(data2)])
	vmax = max([max(data1),max(data2)])
	return vmin, vmax

def draw_map(stname,stlos,stlas,data,plttype,time,year,period,vmin,vmax):
	# Create a Stamen terrain background instance.
	stamen_terrain = cimgt.Stamen('terrain-background')
	fig = plt.figure(figsize=(8,6))
	# Create a GeoAxes in the tile's projection.
	ax = fig.add_subplot(1, 1, 1, projection=stamen_terrain.crs)
	# Limit the extent of the map to a small longitude/latitude range.
	ax.set_extent([7.0, 18.5, 36.5, 47], crs=ccrs.Geodetic())
	# Add the Stamen data at zoom level 8.
	ax.add_image(stamen_terrain, 8)
	# Add data points
	day_map = ax.scatter(stlos, stlas, marker='^', c=data,
	 s=6, alpha=0.7, transform=ccrs.Geodetic(), 
	 cmap='jet', vmax=vmax) #seismic   vmin=vmin, 

	# for i, txt in enumerate(stname):
	# 	ax.text(x=stlos[i],y=stlas[i],s=txt, transform=ccrs.Geodetic())
	# Colorbar
	fig.colorbar(day_map)

	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	# Show Map
	# plt.show()
	# ax.set_title(time + '\n' + period)
	# plt.show()
	if plttype == 'Residual':
		if year not in os.listdir('../Figures/Weekday_Weekend_Residual'):
			os.mkdir('../Figures/Weekday_Weekend_Residual/' + year)
		if time not in os.listdir('../Figures/Weekday_Weekend_Residual/' + year):
			os.mkdir('../Figures/Weekday_Weekend_Residual/' + year + '/' + time)
		plt.savefig('../Figures/Weekday_Weekend_Residual/' + year + '/' + time + '/' + year + '_' + period.replace('.','_') + '.png',dpi=300, bbox_inches='tight')
	elif plttype == 'General':
		if year not in os.listdir('../Figures/Weekday_Weekend'):
			os.mkdir('../Figures/Weekday_Weekend/' + year)
		if time not in os.listdir('../Figures/Weekday_Weekend/' + year):
			os.mkdir('../Figures/Weekday_Weekend/' + year + '/' + time)
		plt.savefig('../Figures/Weekday_Weekend/' + year + '/' + time + '/' + year + '_' + period.replace('.','_') + '.png',dpi=300, bbox_inches='tight')
	plt.close('all')
	return


dpc_db = pd.read_csv('../DBs/dpc.csv')

# List Results
syear1 = '2019'
# iyear = int(syear)
days = glob.glob('../DBs/sens_only/' + syear1 + '/*')

syear2 = '2022'
# iyear = int(syear)
days += glob.glob('../DBs/sens_only/' + syear2 + '/*')


syear = syear1 + syear2


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
vmins = [-135,-135,-135,-135,-135,-135]
vmaxs = [-91.5,-97.41,-115,-120,-108,-97]

for period, s_inx, vmin, vmax in zip(s_strs,s_inxs, vmins, vmaxs):
	# Result List
	res_list = []
	progress = ProgressBar(max_value=len(days))
	for day_date in progress(days):
		sday = day_date.split('/')[-1]
		day_date_int = int(sday)
		# sday = day_date.split('/')[-1]
		# day_date_int = int(sday)
		npzs = glob.glob(day_date + '/*')
		for npz in npzs:
			try:
			# if True:
				# jday = npz.split('/')[-1].split('_')[-1].split('.')[0]
				# ijday = int(jday)
				fmt = '%Y %j'
				ssyear = npz.split('/')[-3]
				d = datetime.strptime(ssyear + ' ' + sday, fmt)
				sta = npz.split('/')[-1].split('.')[0]

				res = np.load(npz)
				keys = list(res.keys())
				pn = res[keys[0]]
				st_inx = dpc_db[dpc_db['calibration.sta'] == sta].index.tolist()[0]
				stla = dpc_db['site.lat'][st_inx]
				stlo = dpc_db['site.lon'][st_inx]
				
				# Weekend
				weekend_vals = []; weekday_vals = []; whole_week = []
				if d.weekday() > 4:
					for trange in keys[1:]:
						weekend_vals.append(res[trange][s_inx])
					res_list.append([stla,stlo,sta,average(weekend_vals),'Weekend'])
				# Weekday
				else:
					for trange in keys[1:]:
						weekday_vals.append(res[trange][s_inx])
					res_list.append([stla,stlo,sta,average(weekday_vals),'Weekday'])
				# Whole Week
				for trange in keys[1:]:
					whole_week.append(res[trange][s_inx])
				res_list.append([stla,stlo,sta,average(whole_week),'Whole Week'])

			except:
				print('Error:',npz)
				continue
		

	res = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	# Drop Outliears
	res = res[~res['STNAME'].isin(['CES','SLD'])]
	weekday = res[res.LABEL == 'Weekday']
	weekday = weekday.groupby(['STNAME','STLA','STLO'], as_index=False, sort=False)['VAL'].mean()
	weekend = res[res.LABEL == 'Weekend']
	weekend = weekend.groupby(['STNAME','STLA','STLO'], as_index=False, sort=False)['VAL'].mean()
	wholeweek = res[res.LABEL == 'Whole Week']
	wholeweek = wholeweek.groupby(['STNAME','STLA','STLO'], as_index=False, sort=False)['VAL'].mean()

	plttype = 'General'
	if plttype == 'Residual':
		median_weekday = np.nanmedian(weekday.VAL)
		median_weekend = np.nanmedian(weekend.VAL)
		median_wholeweek = np.nanmedian(wholeweek.VAL)
		median_weekday_vals = weekday.VAL-median_weekday
		median_weekend_vals = weekend.VAL-median_weekend
		median_wholeweek_vals=wholeweek.VAL-median_wholeweek
		# vmin, vmax = minmax(median_weekday_vals,median_weekday_vals)
		vmax = np.percentile(median_weekday_vals, 95)
		draw_map(weekday.STNAME,weekday.STLO,weekday.STLA,median_weekday_vals,plttype,'Weekday',syear,period,vmin=-vmax,vmax=vmax)
		# vmin, vmax = minmax(median_weekend_vals,median_weekend_vals)
		vmax = np.percentile(median_weekend_vals, 95)
		draw_map(weekend.STNAME,weekend.STLO,weekend.STLA,median_weekend_vals,plttype,'Weekend',syear,period,vmin=-vmax,vmax=vmax)
		# vmin, vmax = minmax(median_wholeweek_vals,median_wholeweek_vals)
		vmax = np.percentile(median_wholeweek_vals, 95)
		draw_map(wholeweek.STNAME,wholeweek.STLO,wholeweek.STLA,median_wholeweek_vals,plttype,'Whole Week',syear,period,vmin=-vmax,vmax=vmax)
		# Weekday Weekend Dif
		vmax = np.percentile(weekday.VAL-weekend.VAL, 95)
		draw_map(wholeweek.STNAME,wholeweek.STLO,wholeweek.STLA,weekday.VAL-weekend.VAL,plttype,'Weekday-Weekend',syear,period,vmin=-vmax,vmax=vmax)
	elif plttype == 'General':
		# vmin, vmax = minmax(weekday.VAL,weekday.VAL)
		vmax = np.nanpercentile(weekday.VAL, 95)
		draw_map(weekday.STNAME,weekday.STLO,weekday.STLA,weekday.VAL,plttype,'Weekday',syear,period,vmin=vmax,vmax=vmax)
		# vmin, vmax = minmax(weekend.VAL,weekend.VAL)
		vmax = np.nanpercentile(weekend.VAL, 95)
		draw_map(weekend.STNAME,weekend.STLO,weekend.STLA,weekend.VAL,plttype,'Weekend',syear,period,vmin=vmax,vmax=vmax)
		# vmin, vmax = minmax(wholeweek.VAL,wholeweek.VAL)
		vmax = np.nanpercentile(wholeweek.VAL, 95)
		draw_map(wholeweek.STNAME,wholeweek.STLO,wholeweek.STLA,wholeweek.VAL,plttype,'Whole Week',syear,period,vmin=vmax,vmax=vmax)