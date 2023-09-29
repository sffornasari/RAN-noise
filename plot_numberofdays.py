import glob, os, json, string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import cartopy
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines
import colorcet as cc
from matplotlib.cm import get_cmap


def resize_colobar(event):
	plt.draw()

	posn = ax.get_position()
	cbar_ax.set_position([posn.x0 + posn.width + 0.01, posn.y0,
						  0.04, posn.height])


def draw_map(i,fig,ax,stname,stlos,stlas,data,nw,df):
	global ix_lims
	df_copy = df.copy()
	# Create a Stamen terrain background instance.
	stamen_terrain = cimgt.Stamen('terrain-background')
	# fig = plt.figure(figsize=(8,6))
	# Create a GeoAxes in the tile's projection.
	# ax = fig.add_subplot(1, 1, 1, projection=stamen_terrain.crs)
	# Limit the extent of the map to a small longitude/latitude range.
	ax.set_extent([7.0, 18.5, 36.5, 47], crs=ccrs.Geodetic())
	# Add the Stamen data at zoom level 8.
	ax.add_image(stamen_terrain, 8)
	# Add data points
	# markers = {'IT':'v','IX':'*','RF':'o','NI':'s','RR':'P','HA':'.'}
	# colors  = {'IT':'k','IX':'orange','RF':'r','NI':'b','RR':'k','HA':'brown'}
	cmap_palette = get_cmap('cet_CET_D8')#cc.cet_CET_D8
	markers = {'IT':'D','IX':'*','RF':'o','NI':'o','RR':'o','HA':'o'}
	colors  = {'IT':'k','IX':'orange','RF':'r','NI':'r','RR':'r','HA':'r'}
	for nw in df.Network.unique():
		df_nw = df[df.Network == nw]
		day_map = ax.scatter(df_nw.STLO, df_nw.STLA, marker=markers[nw], c=df_nw.Days,
		 s=6, alpha=0.9, transform=ccrs.Geodetic(), 
		 cmap=cmap_palette, vmin=0, vmax=100) #seismic

	# IX
	if True:
	# if i == 0:
		axins = inset_axes(ax, width="30%", height="30%",loc="center left",
					bbox_to_anchor=(-0.025,-0.43,1,1), bbox_transform=ax.transAxes #2
					,axes_class=cartopy.mpl.geoaxes.GeoAxes, #loc="center left"
				   axes_kwargs=dict(map_projection=cartopy.crs.PlateCarree()))#
		axins.set_extent(ix_lims, crs=ccrs.Geodetic())
		unique_nws = df_copy.Network.unique()[df_copy.Network.unique() != 'IT']
		for nw in unique_nws:
			df_nw = df_copy[df_copy.Network == nw]
			day_map = axins.scatter(df_nw.STLO, df_nw.STLA, marker=markers[nw], c=df_nw.Days,#colors[nw],
			 s=6, alpha=0.9, transform=ccrs.Geodetic(), 
			 cmap=cmap_palette, vmin=0, vmax=100) #seismic
		axins.add_image(stamen_terrain, 8)
		axins.set_xticks([])
		axins.set_yticks([])
		# Point out the area
		ax.add_patch(Rectangle((ix_lims[0], ix_lims[2]), ix_lims[1]-ix_lims[0], ix_lims[3]-ix_lims[2],alpha=1, fill=None, transform=ccrs.Geodetic()))#
		# Lines for the zoomed area
		# ax.plot([ix_lims[0],10.5],[ix_lims[2],39.08], transform=ccrs.Geodetic(),c='k',linewidth=0.5)
		# ax.plot([ix_lims[0],10.5],[ix_lims[2],40.58], transform=ccrs.Geodetic(),c='k',linewidth=0.5)
		ax.plot([ix_lims[0],10.5],[ix_lims[2],36.55], transform=ccrs.Geodetic(),c='k',linewidth=0.5)
		ax.plot([ix_lims[0],10.5],[ix_lims[2],38.08], transform=ccrs.Geodetic(),c='k',linewidth=0.5)
	# RF
	# elif i == 1:

		# p = plt.Rectangle((rf_lims[0], rf_lims[2]), rf_lims[1]-rf_lims[0], rf_lims[-1]-rf_lims[-2], fill=False)
		# p.set_transform(ax.transAxes)
		# p.set_clip_on(False)
		# ax.add_patch(p)
		# day_map.add_patch(Rectangle((rf_lims[0], rf_lims[2]), rf_lims[1]-rf_lims[0], rf_lims[-1]-rf_lims[-2], alpha=1, facecolor='none'))
		axins = inset_axes(ax, width="30%", height="40%", loc="upper right",
					bbox_to_anchor=(0.025,0.147,1,1), bbox_transform=ax.transAxes
					,axes_class=cartopy.mpl.geoaxes.GeoAxes, #, bbox_to_anchor=(17, 47, 0.5, 0.5)
				   axes_kwargs=dict(map_projection=cartopy.crs.PlateCarree()))#
		axins.set_extent(rf_lims, crs=ccrs.Geodetic())
		# # Move rectangle to upper edge
		# pos1 = axins.get_position() # get the original position 
		# pos2 = [pos1.x0 + 0.3, pos1.y0,  1, pos1.y1] 
		# axins.set_position(pos2)
		unique_nws = df_copy.Network.unique()[df_copy.Network.unique() != 'IT']
		for nw in unique_nws:
			df_nw = df_copy[df_copy.Network == nw]
			day_map = axins.scatter(df_nw.STLO, df_nw.STLA, marker=markers[nw], c=df_nw.Days,#colors[nw],
			 s=6, alpha=0.9, transform=ccrs.Geodetic(), 
			 cmap=cmap_palette, vmin=0, vmax=100) #seismic
		# Add the Stamen data at zoom level 8.
		axins.add_image(stamen_terrain, 8)
		axins.set_xticks([])
		axins.set_yticks([])
		# Point out the area
		ax.add_patch(Rectangle((rf_lims[0], rf_lims[2]), rf_lims[1]-rf_lims[0], rf_lims[3]-rf_lims[2],alpha=1, fill=None, transform=ccrs.Geodetic()))#
		# Lines for the zoomed area
		ax.plot([rf_lims[1],rf_lims[1]+1.1],[rf_lims[2],rf_lims[2]+0.1], transform=ccrs.Geodetic(),c='k',linewidth=0.5)
		ax.plot([rf_lims[1],rf_lims[1]+1.1],[rf_lims[2],47], transform=ccrs.Geodetic(),c='k',linewidth=0.5)

	# # Legend
	if i == 2:
		ix = mlines.Line2D([], [], marker=markers['IX'], linestyle='None',
						  		  markersize=3, label='IX',markerfacecolor='none',markeredgecolor='k') #, color=colors['IX']
		rf = mlines.Line2D([], [], marker=markers['RF'], linestyle='None',
								  markersize=3, label='RF',markerfacecolor='none',markeredgecolor='k') #, color=colors['RF']
		it = mlines.Line2D([], [], marker=markers['IT'], linestyle='None',
								  markersize=3, label='IT',markerfacecolor='none',markeredgecolor='k') #, color=colors['IT']
		ax.legend(handles=[it, ix, rf], prop={'size': 6}, loc= 'lower right')
	


	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	# Show Map
	# plt.show()
	# ax.set_title(time + '\n' + period)
	# plt.savefig('../Figures/PSD_' + year + '.png',dpi=300, bbox_inches='tight')
	# plt.show()
	return fig, ax, day_map


# Read Station Info
dpc_db = pd.read_csv('../../DBs/station_attributes.csv')
unique_stas = dpc_db['sta'].unique()

# Use only 2022 stations
indexes = []
for i, station in enumerate(unique_stas):
	npzs = glob.glob('../../DBs/sens_only/2022/**/' + station + '.*')
	if len(npzs) == 0:
		indexes.append(i)
		# unique_stas.remove(station)
unique_stas = np.delete(unique_stas, indexes)
# if 'BEL7' in unique_stas:
# 	print('hey')

# Define Small Figure Limits
extl = 0.2
rf_lims = dpc_db[dpc_db.net == 'RF']['lon'].min()-extl, dpc_db[dpc_db.net == 'RF']['lon'].max()+extl,dpc_db[dpc_db.net == 'RF']['lat'].min()-extl,dpc_db[dpc_db.net == 'RF']['lat'].max()+extl
ix_lims = dpc_db[dpc_db.net == 'IX']['lon'].min()-extl, dpc_db[dpc_db.net == 'IX']['lon'].max()+extl,dpc_db[dpc_db.net == 'IX']['lat'].min()-extl,dpc_db[dpc_db.net == 'IX']['lat'].max()+extl

# Define Figure
# Create a Stamen terrain background instance.
stamen_terrain = cimgt.Stamen('terrain-background')
# fig,axs = plt.subplots(2,3, figsize=(16,10), facecolor='w', edgecolor='k',subplot_kw={'projection': stamen_terrain.crs}, gridspec_kw = {'wspace':0, 'hspace':0.1})
fig,axs = plt.subplots(1,3, figsize=(12,38), facecolor='w', sharex=True, sharey=True, edgecolor='k',subplot_kw={'projection': stamen_terrain.crs})#, , gridspec_kw = {'wspace':0, 'hspace':0.1}
axs = axs.ravel() #(12,38)
# fig.delaxes(axs[-1]) #The indexing is zero-based here
# Annotation
annotations = list(string.ascii_lowercase)

years = ['2019','2020','2022'] # 
for i,year in enumerate(years):
	days = glob.glob('../../DBs/sens_only/' + year + '/*')
	lens = []; stlas = []; stlos = []; nws = [];
	for station in unique_stas:
		npzs = glob.glob('../../DBs/sens_only/' + year + '/**/' + station + '.*') #'/**/'
		no = len(npzs)
		lens.append(no)

		st_inx = dpc_db[dpc_db['sta'] == station].index.tolist()[0]
		stla = dpc_db['lat'][st_inx]
		stlo = dpc_db['lon'][st_inx]
		nw = dpc_db['net'][st_inx]
		if station == 'NAP':
			print(nw,station)
		nws.append(nw)
		stlas.append(stla)
		stlos.append(stlo)


	# dictionary of lists 
	dictionary = {'Station': unique_stas, 'Days': [(x / len(days))*100 for x in lens], 'Network': nws, 'STLA': stlas, 'STLO':stlos} 
	df = pd.DataFrame(dictionary)
	print(year,df.Days.mean())
	# df = df[df.Days > 0]
	# draw_map(df.Station,df.STLO,df.STLA,df.Days,syear)
	fig, ax, day_map = draw_map(i,fig,axs[i],df.Station,df.STLO,df.STLA,df.Days,df.Network,df)
	axs[i].text(-0.05, 1.02, annotations[i] + ')', transform=axs[i].transAxes, size=10)

# Colorbar
p0 = axs[0].get_position().get_points().flatten()
p1 = axs[1].get_position().get_points().flatten()
p2 = axs[2].get_position().get_points().flatten()
ax_cbar = fig.add_axes([p0[0], p0[1]-0.009, 0.775, 0.008])
cbar = plt.colorbar(day_map, cax=ax_cbar, orientation='horizontal')
cbar.set_label('PSD database completeness (%)')

# # Save Figure
# plt.savefig('../../Figures/completedays2.png',dpi=300, bbox_inches='tight')