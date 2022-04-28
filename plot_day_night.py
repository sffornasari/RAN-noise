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
	fig = plt.figure()
	# Create a GeoAxes in the tile's projection.
	ax = fig.add_subplot(1, 1, 1, projection=stamen_terrain.crs)
	# Limit the extent of the map to a small longitude/latitude range.
	ax.set_extent([7.0, 18.5, 36.5, 47], crs=ccrs.Geodetic())
	# Add the Stamen data at zoom level 8.
	ax.add_image(stamen_terrain, 8)
	# Add data points
	day_map = ax.scatter(stlos, stlas, marker='^', c=data,
	 s=6, alpha=0.7, transform=ccrs.Geodetic(), 
	 cmap='seismic', vmin=vmin, vmax=vmax)
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
	ax.set_title(time + '\n' + period)
	if plttype == 'Residual':
		if year not in os.listdir('../Figures/Day_Night_Residual'):
			os.mkdir('../Figures/Day_Night_Residual/' + year)
		if time not in os.listdir('../Figures/Day_Night_Residual/' + year):
			os.mkdir('../Figures/Day_Night_Residual/' + year + '/' + time)
		plt.savefig('../Figures/Day_Night_Residual/' + year + '/' + time + '/' + year + '_' + period + '.png',dpi=300)
	elif plttype == 'General':
		if year not in os.listdir('../Figures/Day_Night_General'):
			os.mkdir('../Figures/Day_Night_General/' + year)
		if time not in os.listdir('../Figures/Day_Night_General/' + year):
			os.mkdir('../Figures/Day_Night_General/' + year + '/' + time)
		plt.savefig('../Figures/Day_Night_General/' + year + '/' + time + '/' + year + '_' + period + '.png',dpi=300)
	plt.close('all')
	return

dpc_db = pd.read_csv('../DBs/dpc.csv')

# List Results
syear = '2020'
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
vmins = [-135,-135,-135,-135,-135,-135]
vmaxs = [-91.5,-97.41,-115,-120,-108,-97]

for period, s_inx, vmin, vmax in zip(s_strs,s_inxs, vmins, vmaxs):
	# Result List
	res_list = []
	progress = ProgressBar(max_value=len(days))
	for day_date in progress(days):
		sday = day_date.split('/')[-1]
		day_date_int = int(sday)
		npzs = glob.glob(day_date + '/*')
		for npz in npzs:
			try:
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
					res_list.append([stla,stlo,sta,average(days_vals),'Day'])
				else:
					res_list.append([stla,stlo,sta,np.NAN,'Day'])
				nights_vals = [];
				if len(nights) > 0:
					for night in nights:
						nights_vals.append(res[night][s_inx])
					res_list.append([stla,stlo,sta,average(nights_vals),'Night'])
				else:
					res_list.append([stla,stlo,sta,np.NAN,'Night'])
			except:
				continue
		

	res = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','VAL','LABEL'])

	day = res[res.LABEL == 'Day']
	day = day.groupby(['STNAME','STLA','STLO'], as_index=False, sort=False)['VAL'].mean()
	night = res[res.LABEL == 'Night']
	night = night.groupby(['STNAME','STLA','STLO'], as_index=False, sort=False)['VAL'].mean()
	plttype = 'General'
	if plttype == 'Residual':
		median_day = np.nanmedian(day.VAL)
		median_night = np.nanmedian(night.VAL)
		median_day_vals = day.VAL-median_day
		median_night_vals = night.VAL-median_night
		# vmin, vmax = minmax(median_day_vals,median_night_vals)
		draw_map(night.STNAME,night.STLO,night.STLA,median_night_vals,plttype,'Night',syear,period,vmin=vmin,vmax=vmax)
		draw_map(day.STNAME,day.STLO,day.STLA,median_day_vals,plttype,'Day',syear,period,vmin=vmin,vmax=vmax)
	elif plttype == 'General':
		# vmin, vmax = minmax(night.VAL,night.VAL)
		draw_map(night.STNAME,night.STLO,night.STLA,night.VAL,plttype,'Night',syear,period,vmin=vmin,vmax=vmax)
		draw_map(day.STNAME,day.STLO,day.STLA,day.VAL,plttype,'Day',syear,period,vmin=vmin,vmax=vmax)