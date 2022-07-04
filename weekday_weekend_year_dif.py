import pandas as pd
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
	# plt.show()
	# plt.tight_layout()
	if 'Weekday_Weekend_' + foldername not in os.listdir('../Figures/'):
		os.mkdir('../Figures/' + 'Weekday_Weekend_' + foldername)
	if time not in os.listdir('../Figures/' + 'Weekday_Weekend_' + foldername):
		os.mkdir('../Figures/' + 'Weekday_Weekend_' + foldername + '/' + time)
	plt.savefig('../Figures/Weekday_Weekend_' + foldername + '/' + time + '/' + period + '.png',dpi=300, bbox_inches='tight')
	plt.close('all')
	return

year0 = '2019'
year1 = '2022'
year2 = '2020'
db_0 = pd.read_csv('../DBs/weekday_weekend_' + year0 + '.csv')
db_1 = pd.read_csv('../DBs/weekday_weekend_' + year1 + '.csv')
frames = [db_0, db_1]
db_1 = pd.concat(frames)
db_2 = pd.read_csv('../DBs/weekday_weekend_' + year2 + '.csv')

# Weekday
weekday_1 = db_1[db_1.LABEL == 'Weekday']
weekday_2 = db_2[db_2.LABEL == 'Weekday']
# Weekend
weekend_1 = db_1[db_1.LABEL == 'Weekend']
weekend_2 = db_2[db_2.LABEL == 'Weekend']

common_stas = list(set(weekday_1.STNAME.unique()) & set(weekday_2.STNAME.unique()) & set(weekend_1.STNAME.unique()) & set(weekend_2.STNAME.unique()))




for period in db_1.PERIOD.unique():
	res_list_weekday = []; res_list_weekend = []; res_list = []
	progress = ProgressBar(max_value=len(common_stas))
	for sta in progress(common_stas):
		# Day
		weekday_av_1 = average(weekday_1[(weekday_1.STNAME == sta) & (weekday_1.PERIOD == period)].VAL)
		weekday_av_2 = average(weekday_2[(weekday_2.STNAME == sta) & (weekday_2.PERIOD == period)].VAL)
		weekday_av_dif = weekday_av_1 - weekday_av_2
		stla = weekday_1[weekday_1.STNAME == sta]['STLA'].unique()[0]
		stlo = weekday_1[weekday_1.STNAME == sta]['STLO'].unique()[0]
		res_list_weekday.append([stla,stlo,sta,weekday_av_dif,'Weekday'])
		# Night
		weekend_av_1 = average(weekend_1[(weekend_1.STNAME == sta) & (weekend_1.PERIOD == period)].VAL)
		weekend_av_2 = average(weekend_2[(weekend_2.STNAME == sta) & (weekend_2.PERIOD == period)].VAL)
		weekend_av_dif = weekend_av_1 - weekend_av_2
		res_list_weekend.append([stla,stlo,sta,weekend_av_dif,'Weekend'])
		# Whole Week
		av_1 = average(db_1[(db_1.STNAME == sta) & (db_1.PERIOD == period)].VAL)
		av_2 = average(db_2[(db_2.STNAME == sta) & (db_2.PERIOD == period)].VAL)
		av_dif = av_1 - av_2
		res_list.append([stla,stlo,sta,av_dif,'Whole Week'])


	# Weekday
	abs_max = 12
	res_weekday = pd.DataFrame(res_list_weekday,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	# abs_max = max(abs(res_weekday.VAL))
	draw_map(res_weekday.STNAME,res_weekday.STLO,res_weekday.STLA,res_weekday.VAL,'Weekday',str(period),-abs_max,abs_max,year0+year1+year2)
	# Weekend
	res_weekend = pd.DataFrame(res_list_weekend,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	# abs_max = max(abs(res_weekend.VAL))
	draw_map(res_weekend.STNAME,res_weekend.STLO,res_weekend.STLA,res_weekend.VAL,'Weekend',str(period),-abs_max,abs_max,year0+year1+year2)
	# Whole Week
	res_whole = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	# abs_max = max(abs(res_whole.VAL))
	draw_map(res_whole.STNAME,res_whole.STLO,res_whole.STLA,res_whole.VAL,'Whole Week',str(period),-abs_max,abs_max,year0+year1+year2)