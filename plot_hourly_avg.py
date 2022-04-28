import numpy as np
import matplotlib.pyplot as plt
import glob, warnings, os
from datetime import datetime, timedelta
from progressbar import ProgressBar
warnings.filterwarnings('ignore')

#Accelerometric noise models (Cauzzi and Clinton, 2013)
def ALNM():
    Pl = [0.01, 1., 10., 150.,]
    lnm = [-135., -135., -130., -118.25,]
    return Pl, lnm   
def AHNM():
    Ph = [0.01, 0.1, 0.22, 0.32, 0.80, 3.8, 4.6, 6.3, 7.1, 150.,]
    hnm = [-91.5, -91.5, -97.41, -110.5, -120., -98., -96.5, -101., -105., -91.25]
    return Ph, hnm

# List Results
syear = '2019'
days = glob.glob('../DBs/sens_only/' + syear + '/*')

pl,lnm = ALNM()
ph,hnm = AHNM()

progress = ProgressBar(max_value=len(days))
for day in progress(days):
	npzs = glob.glob(day + '/*')
	for npz in npzs:
		sta = npz.split('/')[-1].split('.')[0]
		year,jday = npz.split('/')[-1].split('.')[1].split('_')[1:]
		if os.path.exists(os.path.join('../Figures/Hourly_Average',year,jday,sta + '.png')) == False:
		# if True:
			date_time_obj = datetime.strptime(year + '_' + jday, '%Y_%j')
			date = date_time_obj.strftime('%A %d %b %Y')
			res = np.load(npz)
			keys = list(res.keys())
			pn = res[keys[0]]
			colors = plt.cm.rainbow(np.linspace(0, 1, len(keys[1:])))
			fig = plt.figure(figsize=(16, 9),dpi=100)
			for i,psd in enumerate(keys[1:]):
				middle_time = datetime.strptime(psd, '%H_%M') + timedelta(minutes=45)
				plt.plot(pn,res[psd], color=colors[i],label=middle_time.strftime('%H %M') + r'$\pm$45m')
				plt.xlim([0,100])
				plt.xscale('log')
			plt.plot(pl,lnm,'k',label='ALNM')
			plt.plot(ph,hnm,'k--',label='AHNM')
			plt.ylim([-140,-60])
			plt.title(date + '\n' + sta)
			plt.legend(ncol=5)
			# plt.show()
			if year not in os.listdir('../Figures/Hourly_Average'):
				os.mkdir(os.path.join('../Figures/Hourly_Average',year))
			if jday not in os.listdir(os.path.join('../Figures/Hourly_Average',year)):
				os.mkdir(os.path.join('../Figures/Hourly_Average',year,jday))
			plt.savefig(os.path.join('../Figures/Hourly_Average',year,jday,sta + '.png'))
			# plt.show()
			plt.close('all')
