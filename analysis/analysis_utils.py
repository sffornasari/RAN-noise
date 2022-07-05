import pandas as pd
import numpy as np

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
