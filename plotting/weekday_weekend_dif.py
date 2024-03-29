import json
import numpy as np
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

def draw_map(fig,ax,stname,stlos,stlas,data,vmin,vmax):
	# Limit the extent of the map to a small longitude/latitude range.
	ax.set_extent([6.90, 18.55, 36.5, 47], crs=ccrs.Geodetic())
	# Add the Stamen data at zoom level 8.
	ax.add_image(stamen_terrain, 8)
	# Add data points
	day_map = ax.scatter(stlos, stlas, marker='^', c=data,
	 s=18, alpha=0.7, transform=ccrs.Geodetic(), 
	 cmap='seismic', vmin=vmin, vmax=vmax)
	# Colorbar
	ticks = np.linspace(vmin, vmax, 7)
	cbar = plt.colorbar(day_map, ax= ax, orientation='vertical',extend='both',ticks=ticks,format=tick.FormatStrFormatter('%.1f'))
	cbar.ax.tick_params(labelsize=6) 
	cbar.set_label('Power Change (dB)', rotation=90,size=8)
	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	return fig, ax


# Opening JSON file
f = open('../../DBs/RAN_noise_jsons_2022/wd_we_ext.json')
# returns JSON object as 
# a dictionary
data = json.load(f)

# Read Station Info
dpc_db = pd.read_csv('../../DBs/station_attributes.csv')

# Load Completeness
completeness = pd.read_csv('/media/dertuncay/Elements4/Noise_Model/DB/completeness.csv')

# Years
# year1 = '2019'
year2 = '2022'

# Define Figure
# Create a Stamen terrain background instance.
stamen_terrain = cimgt.Stamen('terrain-background')
fig,axs = plt.subplots(2,3, figsize=(16, 10), facecolor='w', edgecolor='k',subplot_kw={'projection': stamen_terrain.crs}, gridspec_kw = {'wspace':0, 'hspace':0.1})
axs = axs.ravel()
# fig.delaxes(axs[-1]) #The indexing is zero-based here
# Annotation
annotations = list(string.ascii_lowercase)

periods = ['0.0992','0.25','0.5','1.0','2.0','5.04']

for per_idx, period in enumerate(periods):
	print(period)
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

	dif = np.array(dif)
	print(np.where(dif>=0)[0].shape,np.where(dif<0)[0].shape)
	print(np.median(dif))
	abs_dif = np.absolute(dif)
	# print(np.median(dif))
	vmax = np.nanpercentile(abs_dif, 95)
	fig, ax = draw_map(fig,axs[per_idx],stnames,stlos,stlas,dif,-vmax,vmax)
	axs[per_idx].text(-0.1, 1.02, annotations[per_idx] + ')', transform=axs[per_idx].transAxes, size=15)

	# LAT-LON Grids
	import cartopy.mpl.ticker as cticker
	axs[per_idx].set_yticks(np.linspace(37,46,4), crs=ccrs.PlateCarree())
	axs[per_idx].set_yticklabels(np.linspace(37,46,4))
	axs[per_idx].yaxis.tick_left()
	axs[per_idx].set_xticks(np.linspace(7,17, 6), crs=ccrs.PlateCarree())
	axs[per_idx].set_xticklabels(np.linspace(7,17, 6))
	axs[per_idx].xaxis.set_tick_params(labelsize=8)
	axs[per_idx].yaxis.set_tick_params(labelsize=8)
	lon_formatter = cticker.LongitudeFormatter(direction_label=False)
	lat_formatter = cticker.LatitudeFormatter(direction_label=False)
	axs[per_idx].yaxis.set_major_formatter(lat_formatter)
	axs[per_idx].xaxis.set_major_formatter(lon_formatter)
	axs[per_idx].grid(linewidth=2, color='black', alpha=0.0, linestyle='--')

	axs[per_idx].text(14.305573-2.8,40.853294,'Naples',c='k',size=12, alpha=0.7, transform=ccrs.Geodetic())
	axs[per_idx].text(13.877513-1.9,40.756883-0.5,'Ischia',c='k',size=12, alpha=0.7, transform=ccrs.Geodetic())
	axs[per_idx].text(16.866667-0.4,41.125278+0.3,'Puglia',c='k',size=12, alpha=0.7, transform=ccrs.Geodetic())
	axs[per_idx].text(15.286586+0.2,37.075474,'Sicily',c='k',size=12, alpha=0.7, transform=ccrs.Geodetic())
	axs[per_idx].text(12.327145,45.438759-0.5,'Po Valley',c='k',size=12, alpha=0.7, transform=ccrs.Geodetic())


axs[-3].text(0.55, -0.08, 'Red = Weekday Noisier', transform=axs[per_idx].transAxes, size=8)
plt.savefig('../../Figures/Dif_Weekday_Weekend2/' + year2 + '/Median/weekdayweekend.png',dpi=300, bbox_inches='tight')