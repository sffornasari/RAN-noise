import pandas as pd
import numpy as np
import mpld3

def merge_otos(otolist):
  """Function to merge the timeseries for a single period
  for different years.
  The files in otolist should be in order.
  """
  moto = {}
    for oto in otolist:
        for sta in oto.keys():
            if not sta in moto:
                moto[sta] = [[],[]]
            moto[sta][0] += list(oto[sta][0])
            moto[sta][1] += list(oto[sta][1])
    return moto
  
def get_coord(df, sta):
    """Function to retrieve the station coordinates from a DataFrame
    given the station name.
    """
    net, sta, lat, lon, elev = df.query(f'sta == "{sta}"').values.tolist()[0]
    return lon, lat

def seasons(oto):
    """Function to separate the values of the timeseries based on the season.
    All the values from each season are outputted in a list.
    """
    winter = {}
    spring = {}
    summer = {}
    autumn = {}
    for sta in oto.keys():
        winter[sta] = []
        spring[sta] = []
        summer[sta] = []
        autumn[sta] = []
        tv = list(zip(*oto[sta]))
        for t, v in tv:
            jday = int(str(int(t))[4:7])
              if jday < 80 or jday > 355:
                  winter[sta].append(v)
              elif jday >= 80 and jday < 172:
                  spring[sta].append(v)
              elif jday >= 172 and jday < 266:
                  summer[sta].append(v)
              elif jday >= 266 and jday < 355:
                  autumn[sta].append(v)
    return winter, spring, summer, autumn

def day_night(oto):
    """Function to separate the values of the timeseries based on the processing window starting time.
    All the values from day/night (all year long) are outputted in a list.
    """
    night = {}
    day = {}
    for sta in oto.keys():
        night[sta] = []
        day[sta] = []
        tv = list(zip(*oto[sta]))
        for t, v in tv:
            h = int(str(int(t))[7:9])
            if True:
                if h < 6 or h > 20:
                    night[sta].append(v)
                elif 8< h < 18:
                    day[sta].append(v)
    return day, night

def day_night_md(oto):
    """Function to compute the median of the medians of the night-day difference.
    For each day the medians of the daytime values and nighttime values are computed (if possible):
    if both values are available, the difference is taken.
    The median of the differences (all year long) is outputted.
    """
    night = {}
    day = {}
    for sta in oto.keys():
        night[sta] = []
        day[sta] = []
        tv = list(zip(*oto[sta]))
        for t, v in tv:
            h = int(str(int(t))[7:9])
            if True:
                if h < 6 or h > 20:
                    night[sta].append(v)
                elif 8< h < 18:
                    day[sta].append(v)
    return day, night
    nightday = {}
    for sta in oto.keys():
        oldd=0
        md = []
        mn = []
        tv = list(zip(*oto[sta]))
        vmd = []
        vmn = []
        for t, v in tv:
            h = int(str(int(t))[7:9])
            d = int(str(int(t))[4:7])
            if d!=oldd:
                if len(vmd)>0 and len(vmn)>0:
                    md.append(np.median(vmd))
                    mn.append(np.median(vmn))
                vmd = []
                vmn = []
            if True:#-150<v<-50:
                if h < 6 or h > 20:
                    vmn.append(v)
                elif 8< h < 18:
                    vmd.append(v)
            oldd = d
        if len(md)>0 and len(mn)>0:
            dnsta = np.array(mn)-np.array(md)
            nightday[sta] = np.median(dnsta)
    return nightday

def day_night_avg(oto):
    """Function to compute the mean of the means of the night-day difference.
    For each day the means of the daytime values and nighttime values are computed (if possible):
    if both values are available, the difference is taken.
    The mean of the differences (all year long) is outputted.
    """
    nightday = {}
    for sta in oto.keys():
        oldd=0
        md = []
        mn = []
        tv = list(zip(*oto[sta]))
        vmd = []
        vmn = []
        for t, v in tv:
            h = int(str(int(t))[7:9])
            d = int(str(int(t))[4:7])
            if d!=oldd:
                if len(vmd)>0 and len(vmn)>0:
                    md.append(np.mean(vmd))
                    mn.append(np.mean(vmn))
                vmd = []
                vmn = []
            if True:#-150<v<-50:
                if h <= 7 or h >= 20:
                    vmn.append(v)
                elif 8<= h <= 18:
                    vmd.append(v)
            oldd = d
        if len(md)>0 and len(mn)>0:
            dnsta = np.array(mn)-np.array(md)
            nightday[sta] = np.mean(dnsta)
    return nightday

def wd_we(oto):
    """WORKS ONLY FOR 2019! Function to separate the values of the timeseries batween weekdays and weekend.
    All the values from each category (all year long) are outputted in a list.
    """
    wd = {}
    we = {}
    for sta in oto.keys():
        wd[sta] = []
        we[sta] = []
        tv = list(zip(*oto[sta]))
        for t, v in tv:
            h = int(str(int(t))[7:9])
            if 8< h < 18:
                if d%7 < 5:
                    wd[sta].append(v)
                elif d == 6:
                    we[sta].append(v)
    return wd, we

def wd_we_md(oto):
    """WORKS ONLY FOR 2019! The days are divided in weekdays and weekend: for each day the median of the values is computed.
    The lists of medians (all year long) is outputted.
    """
    wd = {}
    we = {}
    for sta in oto.keys():
        oldd=0
        wd[sta] = []
        we[sta] = []
        tv = list(zip(*oto[sta]))
        vmd = []
        for t, v in tv:
            #h = int(str(int(t))[7:9])
            d = int(str(int(t))[4:7])
            if d!=oldd:
                if len(vmd)>0:
                    if oldd%7 < 5:
                        wd[sta].append(np.mean(vmd))
                        vmd = []
                    else:
                        we[sta].append(np.mean(vmd))
                        vmd = []
            if True:
                if True:
                    vmd.append(v)
            oldd = d
    return wd, we

###
def plot_mpld3_ita(attrdict, P, dpc, basemap=None, title='', tiplabel='Attributes', outfile=''):
    """attrdict = {P1:{sta1:v1, sta2:v2,...}, P2:{sta1:v1, sta2:v2,...}, ...} dict of dicts containing the attributes to be plotted.
    P = list of periods of interest [max 11 otherwise modify subplot].
    dpc = DataFrame containing info about the station location.
    basemap (optional) = path to the basemap to be plotted.
    """
    if outfile == '':
        print('outfile attribute must be defined!')
        return
    img_extent = (6.5465398029999999, 18.5205398029999984, 35.4912308440000004, 47.0932308439999971)
    fig = plt.figure(figsize=(25, 12))

    n = 0
    for n, Pk in enumerate(P):
        coord = [get_coord(dpc, sta) for sta in attrdict[Pk].keys()]
        x, y = zip(*coord)

        ax = plt.subplot(3, 4, n+1)
        ax.set_aspect(1)
        ax.set_xmargin(0.05)
        ax.set_ymargin(0.10)
        if basemap != None:
            img = plt.imread(basemap)              
            ax.imshow(img, origin='upper', extent=img_extent)
        vminmax = np.percentile(np.abs(list(attrdict[Pk].values())), 95)
        dd = ax.scatter(x,y,c=list(attrdict[Pk].values()), vmin=-vminmax, vmax=vminmax, cmap='seismic_r', s=10, marker='o', edgecolor='k', linewidths=0.5)
        fig.colorbar(dd,
            orientation='vertical',
            label="Power change (dB)",
            ax=ax,
            extend = 'both')
        labels = []
        for i, st in enumerate(attrdict[Pk].keys()):
            label = sattr.query(f'sta=="{st}"')[['net', 'sta', 'lito_code']]
            label.columns = ['Network', 'Station', 'Litology']
            label['Difference'] = f'{np.round(attrdict[Pk][st], 2)}dB'
            label = label.T
            label.columns = [tiplabel]
            labels.append(str(label.to_html()))
        tooltip = mpld3.plugins.PointHTMLTooltip(dd, labels,
                                       voffset=10, hoffset=10, css=css)
        mpld3.plugins.connect(fig, tooltip)

        ax.set_title(f'Period: {Pk}s')
    ax = plt.subplot(3, 4, n+1)
    proxy = [ax.add_patch(mpl.patches.Rectangle((0,0),1,1,fc = np.array(fc)/255)) for fc in lito_colors.values()]
    labels = lito_colors.keys()
    leg = ax.legend(proxy, labels, loc='center', framealpha=1.0, ncol=3, fontsize=12, title='Litology:')
    leg._legend_box.align = "left"
    ax.set_xlim(-100,100)
    ax.set_ylim(-100,100)
    ax.axis('off')
    plt.tight_layout()
    if title != '':
        htmltxt = mpld3.fig_to_html(fig)
        htmltxt = htmltxt.replace("</style>", f'</style>\n<h1 style="text-align: center">{title}</h1>')
        with open(outfile, 'w') as f:
            f.write(htmltxt)
    else:
        mpld3.save_html(fig, outfile)
    return
