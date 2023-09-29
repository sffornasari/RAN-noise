#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

import json
import mpld3

def get_coord(df, sta):
    stats = df.query(f'sta == "{sta}"').values.tolist()[0]
    return stats[3], stats[2]

lito_code = {
    1 : "Ad",
    2 : "CM",
    3 : "Al",
    4 : "Gd",
    5 : "E",
    6 : "Ssr",
    7 : "Mw",
    8 : "Li",
    9 : "Lb",
    10: "M",
    11: "Pr",
    12: "Cr",
    13: "Ir",
    14: "Nsr",
    15: "Sr",
    16: "Ccr",
    17: "Ucr",
    18: "Ssr",
    20: "B",
}

lito_names_full = {
    "Ad" : "Anthropogenic deposits",
    "CM" : "Chaotic – melange",
    "Al" : "Alluvial deposits",
    "Gd" : "Glacial drift",
    "E"  : "Evaporite",
    "Ssr": "Siliciclastic sedimentary rocks",
    "Mw" : "Mass wasting material",
    "Li" : "Lakes and Ice",
    "Lb" : "Lavas and basalts",
    "M"  : "Marlstone",
    "Pr" : "Pyroclastic rocks",
    "Cr" : "Carbonate rocks",
    "Ir" : "Intrusive rocks",
    "Nsr": "Non-schistose metamorphic rocks",
    "Sr" : "Schistose metamorphic rocks",
    "Ccr": "Consolidated clastic rocks",
    "Ucr": "Unconsolidated clastic rock",
    "Ssr": "Siliciclastic sedimentary rocks",
    "B"  : "Beaches and coastal deposits",
}


lito_colors = {
    "Ad": (117,137,194,255),
    "CM": (202,116,24,255),
    "Al": (168,221,246,255),
    "Gd": (18,1,198,255),
    "E": (243,169,9,255),
    "Mw": (7,7,7,255),
    "Li": (26,207,254,255),
    "Lb": (251,18,0,255),
    "M": (104,48,19,255),
    "Pr": (209,130,158,255),
    "Cr": (234,215,197,255),
    "Ir": (217,23,129,255),
    "Nsr": (240,70,221,255),
    "Sr": (108,55,231,255),
    "Ccr": (243,234,17,255),
    "Ucr": (244,245,192,255),
    "Ssr": (89,191,156,255),
    "B": (250,251,22,255),

}



#%%
# Define some CSS to control our custom labels
css = """
table
{
border-collapse: collapse;
}
th{
color: #ffffff;
background-color: #000000;
}
td{
background-color: #cccccc;
}
table, th, td{
  font-family:Arial, Helvetica, sans-serif;
  border: 1px solid black;
  text-align: right;
}
"""

with open('yearly_median_ext.json', 'r') as f:
    jj = json.load(f)

P = ['0.0992', '0.25', '0.5', '1.0', '2.0', '5.04']
Plabels = {'0.0992':'0.1', '0.25':'0.25', '0.5':'0.5', '1.0':'1.0', '2.0':'2.0', '5.04':'5.0'}

sattr = pd.read_csv('station_attributes.csv')

#%%
mode = 'percentile'
img_extent = (6.5465398029999999, 18.5205398029999984, 35.4912308440000004, 47.0932308439999971)
img = plt.imread('rastered_lito_italy_01_rend.tif')#Basemap from Bucci et al. (2022)        
fig, axs = plt.subplots(4,3, figsize=(20, 12),
                        gridspec_kw={'height_ratios': [1, 1, 1, 0.2], 'width_ratios': [1, 1, 1]})
# axs = fig.add_subplot(axs[0, :])
plt.rcParams.update({'font.size': 14})
n = 0
xlims = {0:[8.5, 13.5], 1:[12, 14], 2:[13.75, 15.25]}
ylims = {0:[43.75, 46.25], 1:[45.75, 46.75], 2:[40.5, 41.25]}
for reg in range(3):
    for Pk in ['0.0992', '0.25', '0.5']:
        coord = [get_coord(sattr, sta) for sta in jj[Pk].keys()]
        x, y = zip(*coord)
        ax = axs[n//3, n%3]


        ax.set_xmargin(0.05)
        ax.set_ymargin(0.10)

        ax.imshow(img, origin='upper', extent=img_extent)
        vmax = np.percentile(list(jj[Pk].values()), 95)
        vmin = np.percentile(list(jj[Pk].values()), 5)

        sortidx = np.argsort(list(jj[Pk].values()))

        if mode == 'percent':
            perc = int(np.round(0.1*len(sortidx)))
            topidx = sortidx[-perc:]
            bottomidx = sortidx[:perc]
        if mode == 'percentile':
            topidx = np.where(list(jj[Pk].values())>np.percentile(list(jj[Pk].values()), 90))
            bottomidx = np.where(list(jj[Pk].values())<np.percentile(list(jj[Pk].values()), 10))
        dt = ax.scatter(np.take(x, topidx),np.take(y, topidx), c='w', s=50, marker='o', edgecolor='k', linewidths=2, label='>90-percentile')
        db = ax.scatter(np.take(x, bottomidx), np.take(y, bottomidx), c='k', s=50, marker='D', edgecolor='k', linewidths=2, label='<10-percentile')
        ax.set_xlim(xlims[reg])
        ax.set_ylim(ylims[reg])
        ax.set_xticks(np.linspace(xlims[reg][0], xlims[reg][1],3))
        if reg != 2:
            ax.set_yticks(np.linspace(ylims[reg][0], ylims[reg][1],3))
        else:
            ax.set_yticks(np.linspace(ylims[reg][0], ylims[reg][1],4))
        ax.grid()
        n+=1

gs = axs[1,2].get_gridspec()
# remove the underlying axes
for ax in axs[3, :]:
    ax.remove()
ax = fig.add_subplot(gs[3, :])
proxy = [ax.add_patch(mpl.patches.Rectangle((0,0),1,1,fc = np.array(fc)/255)) for fc in lito_colors.values()]
proxy += [ax.scatter([], [], c='k', s=50, marker='D', edgecolor='k', linewidths=2, label='<10-percentile')]
proxy += [ax.scatter([], [], c='w', s=50, marker='o', edgecolor='k', linewidths=2, label='>90-percentile')]
labels = list(lito_colors.keys())+['<10-percentile', '>90-percentile']
labels = [lito_names_full[k] for k in lito_colors.keys()]+['Top 10% quietest station', 'Top 10% noisiest station']
lito_names_full
leg = ax.legend(proxy, labels, loc='center', framealpha=1.0, ncol=5, fontsize=12, title=None)
leg._legend_box.align = "left"
ax.set_xlim(-100,100)
ax.set_ylim(-100,100)
ax.axis('off')

plt.tight_layout()

plt.savefig('lito_top_percentile_crop.png', dpi=300)
plt.show()
