import pandas as pd
import matplotlib.pyplot as plt
import os
def average(lst):
	return sum(lst)/len(lst)

# Load DB
year = '2022'
path = '../Figures/Dif_Day_Night/'
if os.path.exists(os.path.join(path,year)) == False:
	os.mkdir(os.path.join(path,year))
db = pd.read_csv('../DBs/day_night_' + year + '.csv')

# Weekday
day = db[db.LABEL == 'Day']
# Weekend
night = db[db.LABEL == 'Night']


common_stas = list(set(day.STNAME.unique()) & set(night.STNAME.unique()))


for period in db.PERIOD.unique():
	av_dif = []
	for sta in common_stas:
		day_av = average(day[(day.STNAME == sta) & (day.PERIOD == period)].VAL)
		night_av = average(night[(night.STNAME == sta) & (night.PERIOD == period)].VAL)
		av_dif.append(night_av - day_av)

	plt.scatter(x=range(len(common_stas)),y=av_dif)
	plt.title('Day - Night\n'+str(period))
	# plt.show()
	plt.savefig(path + year + '/' + str(period) + '.png',dpi=300)
	plt.close('all')