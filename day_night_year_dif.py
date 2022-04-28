import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import os
from progressbar import ProgressBar
def average(lst):
	return sum(lst)/len(lst)

def draw_map(stname,stlos,stlas,data,time,period,vmin,vmax):
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
	# plt.show()
	plt.savefig('../Figures/Day_Night_20192020/' + time + '/' + period + '.png',dpi=300)
	plt.close('all')
	return

db_2019 = pd.read_csv('../DBs/day_night_2019.csv')
db_2020 = pd.read_csv('../DBs/day_night_2020.csv')

# Weekday
day_2019 = db_2019[db_2019.LABEL == 'Day']
day_2020 = db_2020[db_2020.LABEL == 'Day']
# Weekend
night_2019 = db_2019[db_2019.LABEL == 'Night']
night_2020 = db_2020[db_2020.LABEL == 'Night']

common_stas = list(set(day_2019.STNAME.unique()) & set(day_2020.STNAME.unique()) & set(night_2019.STNAME.unique()) & set(night_2020.STNAME.unique()))




for period in db_2019.PERIOD.unique():
	res_list_day = []; res_list_night = []; res_list = []
	progress = ProgressBar(max_value=len(common_stas))
	for sta in progress(common_stas):
		# Day
		day_av_2019 = average(day_2019[(day_2019.STNAME == sta) & (day_2019.PERIOD == period)].VAL)
		# day_av_2020 = average(day_2020[(day_2020.STNAME == sta) & (day_2020.PERIOD == period)].VAL)
		# day_av_dif = day_av_2019 - day_av_2020
		stla = day_2019[day_2019.STNAME == sta]['STLA'].unique()[0]
		stlo = day_2019[day_2019.STNAME == sta]['STLO'].unique()[0]
		# res_list_day.append([stla,stlo,sta,day_av_dif,'Day'])
		# # Night
		# night_av_2019 = average(night_2019[(night_2019.STNAME == sta) & (night_2019.PERIOD == period)].VAL)
		# night_av_2020 = average(night_2020[(night_2020.STNAME == sta) & (night_2020.PERIOD == period)].VAL)
		# night_av_dif = night_av_2019 - night_av_2020
		# res_list_night.append([stla,stlo,sta,day_av_dif,'Day'])
		# Whole Day
		av_2019 = average(db_2019[(db_2019.STNAME == sta) & (db_2019.PERIOD == period)].VAL)
		av_2020 = average(db_2020[(db_2020.STNAME == sta) & (db_2020.PERIOD == period)].VAL)
		av_dif = av_2019 - av_2020
		res_list.append([stla,stlo,sta,av_dif,'Whole'])


	# # Day
	# res_day = pd.DataFrame(res_list_day,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	# abs_max = max(abs(res_day.VAL))
	# draw_map(res_day.STNAME,res_day.STLO,res_day.STLA,res_day.VAL,'Day',str(period),-abs_max,abs_max)
	# # Night
	# res_night = pd.DataFrame(res_list_night,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	# abs_max = max(abs(res_night.VAL))
	# draw_map(res_night.STNAME,res_night.STLO,res_night.STLA,res_night.VAL,'Night',str(period),-abs_max,abs_max)
	# Whole Day
	res_whole = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	abs_max = max(abs(res_whole.VAL))
	draw_map(res_whole.STNAME,res_whole.STLO,res_whole.STLA,res_whole.VAL,'Whole Day',str(period),-abs_max,abs_max)