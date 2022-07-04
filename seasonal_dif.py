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
def median(list):
	return np.nanmedian(list)

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
	if 'Season_' + foldername not in os.listdir('../Figures/'):
		os.mkdir('../Figures/' + 'Season_' + foldername)
	if time not in os.listdir('../Figures/' + 'Season_' + foldername):
		os.mkdir('../Figures/' + 'Season_' + foldername + '/' + time)
	plt.savefig('../Figures/Season_' + foldername + '/' + time + '/' + time + '_Season_Dif_' + period + '.png',dpi=300, bbox_inches='tight')
	plt.close('all')
	return

year0 = '2019'

db = pd.read_csv('../DBs/season_' + year0 + '.csv')

# Winter
winter = db[(db.LABEL.isin(['Winter']))]#,'Autumn'
# Summer
summer = db[(db.LABEL.isin(['Summer']))]#,'Spring'

common_stas = list(set(winter.STNAME.unique()) & set(summer.STNAME.unique()))




for period in db.PERIOD.unique():
	res_list = []
	progress = ProgressBar(max_value=len(common_stas))
	for sta in progress(common_stas):
		# Winter
		winter_av = average(winter[(winter.STNAME == sta) & (winter.PERIOD == period)].VAL)
		# Summer
		summer_av = average(summer[(summer.STNAME == sta) & (summer.PERIOD == period)].VAL)
		av_dif = summer_av - winter_av
		stla = winter[winter.STNAME == sta]['STLA'].unique()[0]
		stlo = winter[winter.STNAME == sta]['STLO'].unique()[0]
		res_list.append([stla,stlo,sta,av_dif,'Dif'])

	# Day
	# abs_max = 12
	res = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	abs_max = max(np.absolute(res.VAL))
	abs_dif = np.absolute(res.VAL)
	vmax = np.nanpercentile(abs_dif, 95)
	# abs_max = max(abs(res_day.VAL))
	draw_map(res.STNAME,res.STLO,res.STLA,res.VAL,'Winter_Summer',str(period),-vmax,vmax,year0)