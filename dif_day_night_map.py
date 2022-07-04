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
	if 'Dif_Day_Night' + foldername not in os.listdir('../Figures/'):
		os.mkdir('../Figures/' + 'Dif_Day_Night' + foldername)
	if time not in os.listdir('../Figures/' + 'Dif_Day_Night' + foldername):
		os.mkdir('../Figures/' + 'Dif_Day_Night' + foldername + '/' + time)
	plt.savefig('../Figures/Dif_Day_Night' + foldername + '/' + time + '/Day_Night_Dif_'  + period + '.png',dpi=300, bbox_inches='tight')
	plt.close('all')
	return

# Load DB
year1 = '2019'
year2 = '2022'
path = '../Figures/Dif_Day_Night/'
if os.path.exists(os.path.join(path,year1+year2)) == False:
	os.mkdir(os.path.join(path,year1+year2))
db = pd.read_csv('../DBs/day_night_' + year1 + '.csv')
db2 = pd.read_csv('../DBs/day_night_' + year2 + '.csv')
frames = [db, db2]
db = pd.concat(frames)
# Weekday
day = db[db.LABEL == 'Day']
# Weekend
night = db[db.LABEL == 'Night']


common_stas = list(set(day.STNAME.unique()) & set(night.STNAME.unique()))


for period in db.PERIOD.unique():
	av_dif = [];
	stnames = []; stlos = []; stlas = [];
	progress = ProgressBar(max_value=len(common_stas))
	for sta in progress(common_stas):
		day_av = average(day[(day.STNAME == sta) & (day.PERIOD == period)].VAL)
		night_av = average(night[(night.STNAME == sta) & (night.PERIOD == period)].VAL)
		av_dif.append(day_av - night_av)
		stla = day[day.STNAME == sta]['STLA'].unique()[0]
		stlo = day[day.STNAME == sta]['STLO'].unique()[0]
		stnames.append(sta)
		stlos.append(stlo)
		stlas.append(stla)

	av_dif = np.array(av_dif)
	abs_dif = np.absolute(av_dif)
	abs_max = max(np.absolute(av_dif))
	vmax = np.nanpercentile(abs_dif, 95)
	draw_map(stnames,stlos,stlas,av_dif,'Day-Night',str(period),-vmax,vmax,year1+year2)
	# plt.scatter(x=range(len(common_stas)),y=av_dif)
	# plt.title('Day - Night\n'+str(period))
	# # plt.show()
	# plt.savefig(path + year1+year2 + '/' + str(period) + '.png',dpi=300)
	# plt.close('all')