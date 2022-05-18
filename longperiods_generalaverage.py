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

def draw_map(stname,stlos,stlas,data,period,vmin,vmax,foldername):
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
	 s=10, alpha=0.9, transform=ccrs.Geodetic(), 
	 cmap='jet',vmax=vmax)#, vmin=vmin, vmax=vmax
	# Colorbar
	cbar = fig.colorbar(day_map)
	cbar.set_label(r'Power (db rel. 1 (m/s$^{2}$)$^{2}$/Hz)', rotation=90)
	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	# Show Map
	# plt.show()
	ax.set_title(period)
	# plt.show()
	# plt.tight_layout()
	# if 'Weekday_Weekend_' + foldername not in os.listdir('../Figures/'):
	# 	os.mkdir('../Figures/' + 'Weekday_Weekend_' + foldername)
	# if time not in os.listdir('../Figures/' + 'Weekday_Weekend_' + foldername):
	# 	os.mkdir('../Figures/' + 'Weekday_Weekend_' + foldername + '/' + time)
	plt.savefig('../Figures/General_Average/' + foldername + '_' + period.replace('.','_') + '.png',dpi=300, bbox_inches='tight')
	plt.close('all')
	return

dpc_db = pd.read_csv('../DBs/dpc.csv')

year1 = '2022'
year2 = '2019'
db_2019 = pd.read_csv('../DBs/longperiod_' + year1 + '.csv')
db_2020 = pd.read_csv('../DBs/longperiod_' + year2 + '.csv')

frames = [db_2019, db_2020]
result = pd.concat(frames)

# common_stas = list(set(weekday_2019.STNAME.unique()) & set(weekday_2020.STNAME.unique()) & set(weekend_2019.STNAME.unique()) & set(weekend_2020.STNAME.unique()))

stas = result.STNAME.unique()

vmins = [-129.5,-127.9,-124.1]
vmaxs = [-104.4,-102.5,-98.07]


for period, vmin, vmax in zip(result.PERIOD.unique(), vmins, vmaxs):
	res_list = []
	progress = ProgressBar(max_value=len(stas))
	for sta in progress(stas):
		# Station Information
		st_inx = dpc_db[dpc_db['calibration.sta'] == sta].index.tolist()[0]
		stla = dpc_db['site.lat'][st_inx]
		stlo = dpc_db['site.lon'][st_inx]
		# Average
		av = average(result[(result.STNAME == sta) & (result.PERIOD == period)].VAL)
		res_list.append([stla,stlo,sta,av,'Whole Week'])


	# Weekday
	# abs_max = 12
	# Whole Week
	res_whole = pd.DataFrame(res_list,columns=['STLA','STLO','STNAME','VAL','LABEL'])
	
	high_noise = res_whole[res_whole.VAL > vmax]
	high_len = len(high_noise)
	print(period,high_len,(high_len/len(stas))*100)

	vmax = np.percentile(res_whole.VAL, 95)
	# max_inx = res_whole[res_whole['VAL'] == max(res_whole.VAL)].index#.tolist()[0]
	# res_whole = res_whole.drop(max_inx)
	# print(res_whole.STNAME[max_inx])
	# abs_min = min(abs(res_whole.VAL))
	# abs_max = max(abs(res_whole.VAL))
	draw_map(res_whole.STNAME,res_whole.STLO,res_whole.STLA,res_whole.VAL,str(period),vmax,vmax,year1+year2)