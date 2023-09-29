import numpy as np
from scipy.interpolate import interp1d
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import matplotlib.ticker as tick
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import glob, warnings, os
from datetime import datetime, timedelta
from progressbar import ProgressBar
import string

def draw_map(fig,ax,stname,stlos,stlas,data,vmin,vmax,period):
	# Limit the extent of the map to a small longitude/latitude range.
	# ax.set_extent([6.90, 18.55, 36.5, 47], crs=ccrs.Geodetic())
	# Add the Stamen data at zoom level 8.
	# ax.add_image(stamen_terrain, 8)
	# Add data points
	day_map = ax.scatter(stlos, stlas, marker='^', c=data,
	 s=18, alpha=0.9, transform=ccrs.Geodetic(), 
	 cmap='jet',vmin=vmin,vmax=vmax)
	# Colorbar
	ticks = np.linspace(vmin, vmax, 10)
	cbar = plt.colorbar(day_map, ax= ax, orientation='vertical',ticks=ticks,format=tick.FormatStrFormatter('%.1f'))
	cbar.ax.tick_params(labelsize=6) 
	cbar.set_label(r'Power (db rel. 1 (m/s$^{2}$)$^{2}$/Hz)', rotation=90, size=8)
	ax.set_title('Period: {} s'.format(period))
	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	return fig, ax, day_map


# Opening JSON file
f = open('../../DBs/RAN_noise_jsons_2022/yearly_median_all.json')
# returns JSON object as 
# a dictionary
data = json.load(f)

# Read Station Info
dpc_db = pd.read_csv('../../DBs/station_attributes.csv')

# Load Completeness
completeness = pd.read_csv('/media/dertuncay/Elements6/Noise_Model/DB/completeness.csv')

# Define Figure
# Create a Stamen terrain background instance.
stamen_terrain = cimgt.Stamen('terrain-background')

# Annotation
import roman


x_low = [0.01,0.1,10,150]
y_low = [-135,-135,-130,-118.25]
x_high = [0.01,0.1,0.22,0.32,0.80,3.8,4.6,6.3,7.1,150]
y_high = [-91.5,-91.5,-97.41,-110.5,-120,-98,-96.5,-101,-105,-91.25]

f1_low = interp1d(x_low, y_low, kind='linear')
f1_high = interp1d(x_high, y_high, kind='linear')

periods = [i for i in data.keys()][:-9]
periods_float = [float(i) for i in data.keys()][:-9]
vmins = [f1_low(period).tolist() for period in periods]
vmaxs = [f1_high(period).tolist() for period in periods]


for per_idx, (period, vmin, vmax) in enumerate(zip(periods,vmins,vmaxs)):
	print(period)
	fig,ax = plt.subplots(1,1, figsize=(8, 8), facecolor='w', edgecolor='k',subplot_kw={'projection': stamen_terrain.crs}, gridspec_kw = {'wspace':0, 'hspace':0.1})
	ax.set_extent([6.90, 18.55, 36.5, 47], crs=ccrs.Geodetic())
	ax.add_image(stamen_terrain, 8)
	stnames = []; stlos = []; stlas = []; dif = []; 
	for sta in data[period]:
		if sta in completeness[completeness.Percentage >= 50].Sta.tolist():
			val = data[period][sta]
			st_inx = dpc_db[dpc_db['sta'] == sta].index.tolist()[0]
			stla = dpc_db['lat'][st_inx]
			stlo = dpc_db['lon'][st_inx]
			stlas.append(stla)
			stlos.append(stlo)
			stnames.append(sta)
			dif.append(val)

	# print(period,(np.array(dif) > vmax).sum())
	fig, ax, day_map = draw_map(fig,ax,stnames,stlos,stlas,dif,vmin,vmax,period)
	# LAT-LON Grids
	import cartopy.mpl.ticker as cticker
	ax.set_yticks(np.linspace(37,46,4), crs=ccrs.PlateCarree())
	ax.set_yticklabels(np.linspace(37,46,4))
	ax.yaxis.tick_left()
	ax.set_xticks(np.linspace(7,17, 6), crs=ccrs.PlateCarree())
	ax.set_xticklabels(np.linspace(7,17, 6))
	ax.xaxis.set_tick_params(labelsize=8)
	ax.yaxis.set_tick_params(labelsize=8)
	lon_formatter = cticker.LongitudeFormatter(direction_label=False)
	lat_formatter = cticker.LatitudeFormatter(direction_label=False)
	ax.yaxis.set_major_formatter(lat_formatter)
	ax.xaxis.set_major_formatter(lon_formatter)
	ax.grid(linewidth=2, color='black', alpha=0.0, linestyle='--')
	ax.text(-0.05, 1.02, roman.toRoman(per_idx) + ')', transform=ax.transAxes, size=15)

	plt.savefig('../../Figures/General_Average2/' + str(period).replace('.','_') + '.png',dpi=100, bbox_inches='tight')
	plt.close('all')
	# plt.show()