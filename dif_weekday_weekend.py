import pandas as pd
import matplotlib.pyplot as plt
import os
def average(lst):
	return sum(lst)/len(lst)

# Load DB
year = '2022'
path = '../Figures/Dif_Weekday_Weekend/'
if os.path.exists(os.path.join(path,year)) == False:
	os.mkdir(os.path.join(path,year))
db = pd.read_csv('../DBs/weekday_weekend_' + year + '.csv')

# Weekday
weekday = db[db.LABEL == 'Weekday']
# Weekend
weekend = db[db.LABEL == 'Weekend']


common_stas = list(set(weekday.STNAME.unique()) & set(weekend.STNAME.unique()))


for period in db.PERIOD.unique():
	av_dif = []
	for sta in common_stas:
		# print(weekday[(weekday.STNAME == sta) & (weekday.PERIOD == period)])
		weekday_av = average(weekday[(weekday.STNAME == sta) & (weekday.PERIOD == period)].VAL)
		weekend_av = average(weekend[(weekend.STNAME == sta) & (weekend.PERIOD == period)].VAL)
		av_dif.append(weekend_av - weekday_av)

	plt.scatter(x=range(len(common_stas)),y=av_dif)
	plt.title('Weekday - Weekend\n'+str(period))
	# plt.show()
	plt.savefig(path + year + '/' + str(period) + '.png',dpi=300)
	plt.close('all')