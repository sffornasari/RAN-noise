import glob, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

def draw_map(stname,stlos,stlas,data, year):
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
	 s=12, alpha=0.9, transform=ccrs.Geodetic(), 
	 cmap='viridis_r', vmin=min(data), vmax=100) #seismic

	# for i, txt in enumerate(stname):
	# 	ax.text(x=stlos[i],y=stlas[i],s=txt, transform=ccrs.Geodetic())
	# Colorbar
	cbar = fig.colorbar(day_map)
	cbar.set_label('PSD database completeness (%)', rotation=270)
	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	# Show Map
	# plt.show()
	# ax.set_title(time + '\n' + period)
	plt.savefig('../Figures/PSD_' + year + '.png',dpi=300, bbox_inches='tight')
	# plt.show()
	return

syear = '2022'
days = glob.glob('../DBs/sens_only/' + syear + '/*')

dpc_db = pd.read_csv('../DBs/dpc.csv')


unique_stas = dpc_db['calibration.sta'].unique()

lens = []; stlas = []; stlos = []
for station in unique_stas:
	npzs = glob.glob('../DBs/sens_only/' + syear + '/**/' + station + '.*')
	no = len(npzs)
	lens.append(no)

	st_inx = dpc_db[dpc_db['calibration.sta'] == station].index.tolist()[0]
	stla = dpc_db['site.lat'][st_inx]
	stlo = dpc_db['site.lon'][st_inx]
	stlas.append(stla)
	stlos.append(stlo)


# dictionary of lists 

dict = {'Station': unique_stas, 'Days': [(x / len(days))*100 for x in lens], 'STLA': stlas, 'STLO':stlos} 
df = pd.DataFrame(dict)
df = df[df.Days > 0]

    
draw_map(df.Station,df.STLO,df.STLA,df.Days,syear)