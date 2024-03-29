import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

###DATA###
# Original
# T = {'Anthony et al.\n(2022)': {'cn':(0.183, 0.218, 1.0/3), 'wn':(0.183, 0.218, 1.0/3), 'sw':(0.183, 0.218, 1.0/3),
#                                'cn_': (0.917, 1.091, 1.0/3), 'wn_': (0.917, 1.091, 1.0/3), 'sw_': (0.917, 1.091, 1.0/3),
#                                'sr':(4.585, 5.453, 1.0), 'sr_': (16.506, 19.629, 1.0),
#                                'pi':(32.095, 38.168, 1.0), 'pi_': (68.775, 81.788, 1.0)},
#      "D\'Alessandro et al.\n(2020)": {'cn': (0.03, 1, 1), 'sw': (1, 10, 0.5), 'wn': (1, 10, 0.5), 'sr': (10, 40, 1)},
#      'Cauzzi et al.\n(2014)': {'em':(0, 0.1, 0.5), 'cn': (0.05, 3, 0.5), 'sw': (3, 7, 1), 'in': (7, 100, 1)},
#      'Bonnefoy-Claudet et al.\n(2006)': {'cn':(0, 1, 0.25), 'wn': (0.2, 1, 0.25), 'sw': (0.2, 6.5, 0.25), 'sr':(0.8, 2, 0.25), 'pi': (1, 100, 0.5)},
#      'McNamara & Buland\n(2004)': {'cn':(0.1, 1, 1), 'sr': (4, 8, 1), 'sw': (10, 16, 1)},
#     }

# Revision1
T = {'Anthony et al.\n(2022)': {'cn':(0.183, 1.091, 1.0/3), 'wn':(0.183, 1.091, 1.0/3), 'sw':(0.183, 1.091, 1.0/3),
                               'sr':(4.585, 19.629, 1.0), 'pi':(32.095, 81.788, 1.0)},
     "D\'Alessandro et al.\n(2021)": {'cn': (0.03, 1, 1), 'sw': (1, 10, 0.5), 'wn': (1, 10, 0.5), 'sr': (10, 40, 1)},
     'Cauzzi & Clinton\n(2013)': {'em':(0, 0.1, 0.5), 'cn': (0.05, 3, 0.5), 'sw': (3, 7, 1), 'in': (7, 100, 1)},
     'Bonnefoy-Claudet et al.\n(2006)': {'cn':(0, 1, 0.25), 'wn': (0.2, 1, 0.25), 'sw': (0.2, 6.5, 0.25), 'sr':(0.8, 2, 0.25), 'pi': (1, 100, 0.5)},
     'McNamara & Buland\n(2004)': {'cn':(0.1, 1, 1), 'sr': (4, 8, 1), 'sw': (10, 16, 1)},
    }

colors = {'em':0.8, 'cn':0.1, 'wn': 0.2, 'sw': 0.9, 'sr': 0.0, 'in': 0.7, 'pi': 0.3}
labels = {'em':'Electromagnetic noise', 'cn': 'Cultural noise', 'in': 'Instrumental noise', 'wn': 'Wind related', 'pi': 'Pressure induced', 'sw': 'Swell related', 'sr': 'Sea related'}

##### PLOT #####
fig, ax = plt.subplots(1, figsize=(16,6))
#ax.set_facecolor('#36454F')

# bars
#Axes.barh(y, width, height=0.8, left=None, *, align='center', **kwargs)[source]

y = 0

for paper,classification in T.items():
    p = 1
    py = 1
    ax.hlines(y, 0, 1000, colors='k', linestyles='solid')
    for k,v in classification.items():
        dt = v[1]-v[0]
        if p>0.9:
            p = 0
            py = 0
        else:
            py += 1
        ax.barh(y+py*v[2], dt, align='edge', height=v[2], left=v[0], color=mpl.cm.tab20(colors[k[:2]]), hatch='', alpha=0.6)
        p += v[2]
    y += 1.1
    ax.hlines(y-0.1, 0, 1000, colors='k', linestyles='solid')

# grid lines
ax.set_axisbelow(True)
ax.xaxis.grid(color='k', linestyle='dashed', alpha=0.4, which='both')

# align x axis
ax.set_xlim(0.021, 121)
ax.set_xscale('log')

# remove spines

ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['left'].set_position(('outward', 10))
ax.spines['top'].set_visible(False)
#ax.spines['bottom'].set_color('w')

ax.tick_params(axis='both', which='both', labelsize=14,
               bottom=False, top=False, labelbottom=True,
               left=False, right=False, labelleft=True)

papers = T.keys()
ax.set_yticks(np.arange(0.5, len(papers), 1.1), labels=papers)
ax.set_xticks([0.1, 1, 10, 100], labels=[str(t) for t in [0.1, 1, 10, 100]])
ax.xaxis.set_label_position('bottom')
ax.xaxis.tick_bottom()
ax.set_xlabel('Period [s]', loc='center', fontsize=14)

##### LEGENDS #####
legend_elements = [Patch(facecolor=mpl.cm.tab20(colors[k]), label=v,  hatch='', alpha=0.6) for k,v in labels.items()]

legend = ax.legend(handles=legend_elements, loc='lower center', ncol=7, frameon=False, bbox_to_anchor=(0.446, 1.0), fontsize=12,)
plt.setp(legend.get_texts(), color='k')
plt.savefig('noisesources_rev2.png', dpi=300)


##### PLOT #####
fig, ax = plt.subplots(1, figsize=(16,6))
#ax.set_facecolor('#36454F')

otos = [[0.088, 0.099,  0.111],
[0.223, 0.250,  0.281],
[0.445, 0.500,  0.561],
[0.891, 1.000,  1.122],
[1.782, 2.000,  2.245],
[4.490, 5.040,  5.657],
[7.127, 8.000,  8.980],
[14.254, 16.000,  17.959],
[28.509, 32.000,  35.919],
[71.838, 80.635,  90.510],]

# bars
#Axes.barh(y, width, height=0.8, left=None, *, align='center', **kwargs)[source]

y = 0

for paper,classification in T.items():
    p = 1
    py = 1
    ax.hlines(y, 0, 1000, colors='k', linestyles='solid')
    for k,v in classification.items():
        dt = v[1]-v[0]
        if p>0.9:
            p = 0
            py = 0
        else:
            py += 1
        ax.barh(y+py*v[2], dt, align='edge', height=v[2], left=v[0], color=mpl.cm.tab20(colors[k[:2]]), hatch='', alpha=0.6)
        p += v[2]
    # for oto in otos:
    #     ax.fill_between([oto[0], oto[2]], y, y+1, alpha=0.3, ec='k', fc='None', hatch='xxx')
    y += 1.1
    ax.hlines(y-0.1, 0, 1000, colors='k', linestyles='solid')

# grid lines
ax.set_axisbelow(True)
ax.xaxis.grid(color='k', linestyle='dashed', alpha=0.4, which='both')

# align x axis
ax.set_xlim(0.021, 121)
ax.set_xscale('log')

# remove spines

ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['left'].set_position(('outward', 10))
ax.spines['top'].set_visible(False)
#ax.spines['bottom'].set_color('w')

ax.tick_params(axis='both', which='both', labelsize=14,
               bottom=False, top=False, labelbottom=True,
               left=False, right=False, labelleft=True)

papers = T.keys()
ax.set_yticks(np.arange(0.5, len(papers), 1.1), labels=papers)
ax.set_xticks([0.1, 1, 10, 100], labels=[str(t) for t in [0.1, 1, 10, 100]])
ax.xaxis.set_label_position('bottom')
ax.xaxis.tick_bottom()
ax.set_xlabel('Period [s]', loc='center', fontsize=14)

for oto in otos:
    # ax.axvspan(oto[0], oto[2], alpha=0.5, ec='red', fc='None', hatch='xx')
    ax.fill_between([oto[0], oto[2]], 0, 5.41, alpha=0.3, ec='k', fc='None', hatch='xxx')
##### LEGENDS #####
legend_elements = [Patch(facecolor=mpl.cm.tab20(colors[k]), label=v,  hatch='', alpha=0.6) for k,v in labels.items()]

legend_elements.append(Patch(ec='k', fc='None', hatch='xxx', label='⅓-octave band', alpha=0.3))

legend = ax.legend(handles=legend_elements, loc='lower center', ncol=4, frameon=False, bbox_to_anchor=(0.343, 1.0), fontsize=12,)
plt.setp(legend.get_texts(), color='k')
plt.savefig('noisesources_oto_rev2.png', dpi=300)