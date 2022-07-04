import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import os
from progressbar import ProgressBar
def average(lst):
	return sum(lst)/len(lst)

def draw_map(stname,stlos,stlas,data,time,period,vmin,vmax,foldername):
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
	period = period.replace('.','_')
	# plt.show()
	if 'Day_Night_' + foldername not in os.listdir('../Figures/'):
		os.mkdir('../Figures/' + 'Day_Night_' + foldername)
	if time not in os.listdir('../Figures/' + 'Day_Night_' + foldername):
		os.mkdir('../Figures/' + 'Day_Night_' + foldername + '/' + time)
	plt.savefig('../Figures/Day_Night_' + foldername + '/' + time + '/' + time + '_Covid_Dif_' + period + '.png',dpi=300, bbox_inches='tight')
	plt.close('all')
	return

year0 = '2019'
year1 = '2022'
year2 = '2020'
db_0 = pd.read_csv('../DBs/day_night_' + year0 + '.csv')
db_1 = pd.read_csv('../DBs/day_night_' + year1 + '.csv')
frames = [db_0, db_1]
db_1 = pd.concat(frames)
db_2 = pd.read_csv('../DBs/day_night_' + year2 + '.csv')

# Day
day_1 = db_1[db_1.LABEL == 'Day']
day_2 = db_2[db_2.LABEL == 'Day']
# Night
night_1 = db_1[db_1.LABEL == 'Night']
night_2 = db_2[db_2.LABEL == 'Night']

common_stas = list(set(day_1.STNAME.unique()) & set(day_2.STNAME.unique()) & set(night_1.STNAME.unique()) & set(night_2.STNAME.unique()))




for period in db_1.PERIOD.unique():
	res_list_day = []; res_list_night = []; res_list = []
	progress = ProgressBar(max_value=len(common_stas))
	for sta in progress(common_stas):
		# Day
		day_av_1 = average(day_1[(day_1.STNAME == sta) & (day_1.PERIOD == period)].VAL)
		day_av_2 = average(day_2[(day_2.STNAME == sta) & (day_2.PERIOD == period)].VAL)
		day_av_dif = day_av_1 - day_av_2
		stla = day_1[day_1.STNAME == sta]['STLA'].unique()[0]
		stlo = day_1[day_1.STNAME == sta]['STLO'].unique()[0]
		res_list_day.append([stla,stlo,sta,day_av_dif,'Day'])
		# Night
		night_av_1 = average(night_1[(night_1.STNAME == sta) & (night_1.PERIOD == period)].VAL)
		night_av_2 = average(night_2[(night_2.STNAME == sta) & (night_2.PERIOD == period)].VAL)
		night_av_dif = night_av_1 - night_av_2
		res_list_night.append([stla,stlo,sta,night_av_dif,'Night'])
		# Whole Day
		av_1 = average(db_1[(db_1.STNAME == sta) & (db_1.PERIOD == period)].VAL)
		av_2 = average(db_2[(db_2.STNAME == sta) & (db_2.PERIOD == period)].VAL)
		av_dif = av_1 - av_2
		res_list.append([stla,stlo,sta,av_dif,'Whole'])


	# Day
	# abs_max = 12
	res_day = pd.DataFrame(res_list_day,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	abs_max = max(np.absolute(res_day.VAL))
	abs_dif = np.absolute(res_day.VAL)
	vmax = np.nanpercentile(abs_dif, 95)
	# abs_max = max(abs(res_day.VAL))
	draw_map(res_day.STNAME,res_day.STLO,res_day.STLA,res_day.VAL,'Day',str(period),-vmax,vmax,year0+year1+year2)
	# Night
	res_night = pd.DataFrame(res_list_night,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	abs_max = max(np.absolute(res_night.VAL))
	abs_dif = np.absolute(res_night.VAL)
	vmax = np.nanpercentile(abs_dif, 95)
	# abs_max = max(abs(res_night.VAL))
	draw_map(res_night.STNAME,res_night.STLO,res_night.STLA,res_night.VAL,'Night',str(period),-vmax,vmax,year0+year1+year2)
	# Whole Day
	res_whole = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	abs_max = max(np.absolute(res_whole.VAL))
	abs_dif = np.absolute(res_whole.VAL)
	vmax = np.nanpercentile(abs_dif, 95)
	# abs_max = max(abs(res_whole.VAL))
	draw_map(res_whole.STNAME,res_whole.STLO,res_whole.STLA,res_whole.VAL,'Whole Day',str(period),-vmax,vmax,year0+year1+year2)