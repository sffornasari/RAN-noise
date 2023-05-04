import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

###Plot parameters
singleyear = False
year = 2019
P = 0.0992
cauzzi = True
high_res = True
alwaysactive = True
davlimit = 180


Ps = [0.0992, 0.25, 0.5, 1, 2, 5.04]
Ptitle = [0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
fig = plt.figure(figsize=(30, 15))
outer = gridspec.GridSpec(3, 2, wspace=0.1, hspace=0.4)
for i in range(6):
    inner = gridspec.GridSpecFromSubplotSpec(1, 3,
                    subplot_spec=outer[i], wspace=0.1, hspace=0.1, width_ratios= [305, 66, 175])#[365, 76, 125]
    P = Ps[i]
    if singleyear == False:
        times = ['0000.0',
        '0045',
        '0130',
        '0215',
        '0300',
        '0345',
        '0430',
        '0515',
        '0600',
        '0645',
        '0730',
        '0815',
        '0900',
        '0945',
        '1030',
        '1115',
        '1200',
        '1245',
        '1330',
        '1415',
        '1500',
        '1545',
        '1630',
        '1715',
        '1800',
        '1845',
        '1930',
        '2015',
        '2100',
        '2145',
        '2230',]

        days = {2019:(1,366), 2020:(69, 126), 2022:(1,121)}

        xs = {}
        for year in [2019, 2020, 2022]:
            xs[year] = []
            for d in range(days[year][0], days[year][1]):
                for t in times:
                    xs[year].append(f'{year}{d:03d}{t}')

        keys = []
        for year in [2019, 2020, 2022]:
            oto = np.load(f'/content/drive/MyDrive/oto_P_ts/oto_ts_{P:.2e}_{year}.npz')
            keys += list(oto.keys())
        keys = [*set(keys)]
        keys.sort()

        k19 = np.load(f'/content/drive/MyDrive/oto_P_ts/oto_ts_{P:.2e}_2019.npz').keys()
        k19 = [k for k in k19 if len(np.load(f'/content/drive/MyDrive/oto_P_ts/oto_ts_{P:.2e}_2019.npz')[k][0])>davlimit*31]
        k20 = np.load(f'/content/drive/MyDrive/oto_P_ts/oto_ts_{P:.2e}_2020.npz').keys()
        k22 = np.load(f'/content/drive/MyDrive/oto_P_ts/oto_ts_{P:.2e}_2022.npz').keys()

        if alwaysactive == True:
            keys = [key for key in keys if key in k19 and key in k20 and key in k22]
            import random
            random.seed(43)
            keys = random.choices(keys, k=20)

        multi_ext_ts = {}
        for year in [2019, 2020, 2022]:
            oto = np.load(f'/content/drive/MyDrive/oto_P_ts/oto_ts_{P:.2e}_{year}.npz')
            ext_ts = []
            stas = []
            for k in keys:
                try:
                    ts = oto[k]
                    idx = 0
                    sta_ts = []
                    for x in xs[year]:
                        if float(x) in ts[0]:
                            sta_ts.append(ts[1][idx])
                            idx += 1
                        else:
                            sta_ts.append(np.nan)
                    ext_ts.append(sta_ts)
                except:
                    ext_ts.append([np.nan]*len(xs[year]))
            ext_ts = np.array(ext_ts)
            multi_ext_ts[year] = ext_ts
        if cauzzi == False:
            vmin=np.nanpercentile(ext_ts, 5)
            vmax=np.nanpercentile(ext_ts, 95)
        elif cauzzi == True:
            #Accelerometric noise models (Cauzzi and Clinton, 2013)
            Pl = [0.01, 1., 10., 150.,]
            lnm = [-135., -135., -130., -118.25,]
            if Pl[0]<=P<=Pl[-1]:
                lnm_P = np.interp(P, Pl, lnm)
                vmin = lnm_P
            else:
                print(f'P={P} out of ALNM range.')
                vmin=np.nanpercentile(ext_ts, 5)
            Ph = [0.01, 0.1, 0.22, 0.32, 0.80, 3.8, 4.6, 6.3, 7.1, 150.,]
            hnm = [-91.5, -91.5, -97.41, -110.5, -120., -98., -96.5, -101., -105., -91.25]
            if Ph[0]<=P<=Ph[-1]:    
                hnm_P = np.interp(P, Ph, hnm)
                vmax = hnm_P
            else:
                print(f'P={P} out of ALNM range.')
                vmax=np.nanpercentile(ext_ts, 95)

        xticks = {2019: [0, 961, 1829, 2790, 3720, 4681, 5611, 6572, 7533, 8463, 9424, 10354],
                  2020: [0, 713, 1643],
                  2022: [0, 961, 1829, 2790]}
        xticklabels = {2019: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                      2020: ['March', 'April', 'May'],
                      2022: ['January', 'February', 'March', 'April']}
        titles = {2019:'2019', 2020:'2020 lockdown', 2022:'2022'}
        
        pcms = {}
        gridcell = []
        mpl.rcParams.update({'font.size': 13})
        for j, year in enumerate([2019, 2020, 2022]):
            ax = plt.Subplot(fig, inner[j])
            pcms[year] = ax.pcolormesh(multi_ext_ts[year], vmin=vmin, vmax=vmax, cmap='jet')
            ax.hlines(list(range(1,multi_ext_ts[year].shape[0])),xmin=0, xmax=multi_ext_ts[year].shape[1], color='k', lw=4)
            ax.hlines(list(range(1,multi_ext_ts[year].shape[0])),xmin=0, xmax=multi_ext_ts[year].shape[1], color='white', lw=1)
            ax.set_xticks(xticks[year])
            ax.set_xticklabels([f'{m[:3]}.' if len(m)>4 else m for m in xticklabels[year]], ha='left', rotation=0)
            if j == 0:
                # ax.set_yticks(np.arange(0.5, len(keys)+0.5, 1))
                ax.set_yticks(np.arange(0.5, len(keys)+0.5, 2))
                ax.set_yticklabels(keys[::2])
            elif j == 2:
              ax.yaxis.tick_right()
              ax.yaxis.set_label_position("right")
              ax.set_yticks(np.arange(1.5, len(keys)+0.5, 2))
              ax.set_yticklabels(keys[1::2])
            else:
                ax.set_yticks([])
                ax.set_yticklabels([])
            ax.set_title(titles[year])
            fig.add_subplot(ax)
            gridcell.append(ax)

        xtext = (gridcell[2].get_window_extent().x0+gridcell[2].get_window_extent().width-gridcell[0].get_window_extent().x0)
        ytext = gridcell[0].get_window_extent().y0+gridcell[0].get_window_extent().height*1.12
        inv = fig.transFigure.inverted()
        xtext, ytext = inv.transform((xtext, ytext))
        plt.figtext(xtext+2*(i%2)/5, ytext,f"Period = {Ptitle[i]} s", va="center", ha="right", size=15, weight='bold')
        cbar = fig.colorbar(pcms[2020], ax=ax, orientation='vertical', pad=0.30, aspect=25, extend='both', ticks=np.linspace(int(np.round(vmin+0.5)), int(np.round(vmax-0.5)), 5, dtype=int))
        cbar.set_label('Noise Power (dB)')
        cbar.ax.tick_params(rotation=90)
if high_res == True:
    plt.savefig(f'yearlong.png', dpi=300, bbox_inches='tight',pad_inches=0.1)
elif high_res == False:
    #plt.savefig(f'/content/drive/MyDrive/oto_P_ts/mega_fig_{P:.2e}s_multi_l.png', dpi=100, bbox_inches='tight',pad_inches=0.1)
    # plt.savefig(f'/content/drive/MyDrive/oto_P_ts/mega_fig_selected_l.png', dpi=100, bbox_inches='tight',pad_inches=0.1)
    pass

plt.show()
