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
	 s=6, alpha=0.7, transform=ccrs.Geodetic(), 
	 cmap='seismic', vmin=vmin, vmax=vmax)
	# Colorbar
	ticks = np.linspace(vmin, vmax, 7)
	cbar = plt.colorbar(day_map, ax= ax, orientation='vertical',ticks=ticks,format=tick.FormatStrFormatter('%.1f'))
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
f = open('../DBs/JSON_Final/wd_we_ext.json')
data = json.load(f)

# Read Station Info
dpc_db = pd.read_csv('../DBs/station_attributes.csv')

# Years
year1 = '2019'
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
		val = data[period][sta]
		st_inx = dpc_db[dpc_db['sta'] == sta].index.tolist()[0]
		stla = dpc_db['lat'][st_inx]
		stlo = dpc_db['lon'][st_inx]
		stlas.append(stla)
		stlos.append(stlo)
		stnames.append(sta)
		dif.append(val)

	dif = np.array(dif)
	abs_dif = np.absolute(dif)
	vmax = np.nanpercentile(abs_dif, 95)
	fig, ax = draw_map(fig,axs[per_idx],stnames,stlos,stlas,dif,-vmax,vmax)
	axs[per_idx].text(-0.05, 1.02, annotations[per_idx] + ')', transform=axs[per_idx].transAxes, size=10)


axs[-3].text(0.65, -0.05, 'Red = Weekday Noisier', transform=axs[per_idx].transAxes, size=8)
plt.savefig('../Figures/Figure 7.png',dpi=300, bbox_inches='tight')
