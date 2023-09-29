from dalessandro_res import load_model
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import matplotlib.ticker as tick
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import json

# Load Noise Levels
f = open('../DB/RAN_noise_jsons_2022/yearly_2_5_statistics_all.json')
data = json.load(f)

# Read Station Info
dpc_db = pd.read_csv('../DB/station_attributes.csv')

def draw_map(fig,ax,stname,stlos,stlas,data,vmin,vmax):
	# Limit the extent of the map to a small longitude/latitude range.
	ax.set_extent([6.90, 18.55, 36.5, 47], crs=ccrs.Geodetic())
	# Add the Stamen data at zoom level 8.
	ax.add_image(stamen_terrain, 8)
	# Add data points
	day_map = ax.scatter(stlos, stlas, marker='^', c=data,
	 s=24, alpha=0.9, transform=ccrs.Geodetic(), 
	 cmap='viridis_r',vmin=0,vmax=vmax)
	# Colorbar
	# ticks = np.linspace(vmin, vmax, 7)
	cbar = plt.colorbar(day_map, ax= ax, orientation='vertical',format=tick.FormatStrFormatter('%.1f'),extend='max')#,ticks=ticks
	cbar.ax.tick_params(labelsize=6) 
	cbar.set_label(r'Difference (dB)', rotation=90, size=8)
	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	return fig, ax


# Periods
period_list = list(data.keys())
period_list = np.squeeze(np.array([[float(i) for i in period_list]]))
# Period Limits
limits = {'I':[1/0.025,1/0.12],'II':[1/0.12,1/1.2],'III':[1/1.2,1/10],'IV':[1/10,1/30]}

for band in ['I','II','III','IV']:

	# Map info
	stamen_terrain = cimgt.Stamen('terrain-background')
	fig,axs = plt.subplots(1,1, figsize=(8, 6), facecolor='w', edgecolor='k',subplot_kw={'projection': stamen_terrain.crs}, gridspec_kw = {'wspace':0, 'hspace':0.1})

	# Load Noise Model
	noise_model, xv, yv, f_file = load_model(band)

	period_indexes = np.where(np.logical_and(period_list<=limits[band][0], period_list>=limits[band][1]))

	band_periods = period_list[period_indexes[0]]

	periods = [str(i) for i in band_periods]

	stnames = []; stlos = []; stlas = []; pred_dif = [];
	for sta in data[periods[0]]:
		if sta not in stnames:
			st_inx = dpc_db[dpc_db['sta'] == sta].index.tolist()[0]
			stla = dpc_db['lat'][st_inx]
			stlo = dpc_db['lon'][st_inx]
			stlas.append(stla)
			stlos.append(stlo)
			stnames.append(sta)
			# Ales Prediction
			sta_loc = np.array([stla,stlo])
			ales_pred = noise_model(sta_loc)[0]
			# print(sta,sta_loc,ales_pred)
			vals = [];
			for per_idx, period in enumerate(periods):
				# print(period)
				val = data[period][sta]
				vals.append(val)
			# print(sta,vals,np.median(vals))
			vals = np.median(vals)
			pred_dif.append(vals - ales_pred)


	db = pd.DataFrame({'Station':stnames,'Dif':pred_dif})
	vmax = np.nanpercentile(abs(db.Dif), 95)
	vmin = np.nanpercentile(db.Dif, 5)
	fig, ax = draw_map(fig,axs,db.Station,stlos,stlas,db.Dif,vmin,vmax)
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
	
	plt.savefig('../Figures/Alessandro_Difference/' + band + '.png', dpi=300, bbox_inches='tight')
	plt.close('all')
	''' DON'T SHOW OUTLIERS TO HAVE SMOOTHER RESULTS'''