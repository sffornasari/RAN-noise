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


year1 = '2019'
year2 = '2022'
dif_db = pd.read_csv('../DBs/Dif_Periodwise_' year1 + year2 + '.csv')

stla_stlo = pd.read_csv('../DBs/dpc.csv')

stlas = []; stlos = []
for sta in dif_db.Station:
	st_inx = stla_stlo[stla_stlo['calibration.sta'] == sta].index.tolist()[0]
	stlas.append(stla_stlo['site.lat'][st_inx])
	stlos.append(stla_stlo['site.lon'][st_inx])

maxs = dif_db.max(axis=0)[1:]
mins = dif_db.min(axis=0)[1:]

for val,min_val,max_val in zip(dif_db.columns[1:],mins,maxs):
	vmin, vmax = min(min_val,max_val), max(min_val,max_val)
	vmax = (max(abs(vmin),abs(vmax)))
	vmin = -vmax
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
	day_map = ax.scatter(stlos, stlas, marker='^', c=dif_db[val],
	 s=6, alpha=0.7, transform=ccrs.Geodetic(), 
	 cmap='seismic',vmin=vmin,vmax=vmax)
	# Colorbar
	fig.colorbar(day_map)
	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	# plt.show()
	try:
		plt.savefig('../Figures/Dif_Average/' year1 + year2 + '/' + "{:.3f}".format(round(float(val),3)).zfill(7).replace('.','_') + '.png',dpi=300, bbox_inches='tight')
	except:
		plt.savefig('../Figures/Dif_Average/' year1 + year2 + '/' + val + '.png',dpi=300, bbox_inches='tight')
	plt.close('all')