import numpy as np
import itertools
from scipy.interpolate import RegularGridInterpolator

def load_model(modeltype):
	file = '../DB/DAlessandro_ESS_2019/PythonFriendly/Fig_6_AVG_Z_' + modeltype + '.grd'
# # DIR = '../DB/DAlessandro_ESS_2019/PythonFriendly/
# files = os.listdir(DIR)

# for file in files:
	# print(file)

	# Using readlines()
	# file1 = open(os.path.join(DIR,file), 'r')
	file1 = open(file, 'r')
	Lines = file1.readlines()

	grd_file = []
	for line in Lines[5:-2]:
		words_list = line.split()
		# if len(words_list) > 0:
		for i, word in enumerate(words_list):
			if word == 'NAN':
				words_list[i] = np.nan
			else:
				words_list[i] = float(word)
		grd_file.append(words_list)
		


	empty_rows = [i for i,x in enumerate(grd_file) if not x]
	# Add zero to the beginning
	empty_rows = [0, *empty_rows]


	f_file = []
	for idx in range(len(empty_rows[:-1])):
		merged = list(itertools.chain.from_iterable(grd_file[empty_rows[idx]:empty_rows[idx+1]]))
		f_file.append(merged)

	f_file = np.array(f_file)

	nrows = 131
	ncols = 171
	# Lat Lon Lims
	xmin, xmax = Lines[2].split()
	xmin = float(xmin) - 0.05
	xmax = float(xmax) + 0.05
	ymin, ymax = Lines[3].split()
	ymin = round(float(ymin),2) - 0.05
	ymax = float(ymax) + 0.05
	# print(xmin,xmax)
	# print(ymin,ymax)

	x = np.linspace(xmin, xmax, ncols)
	y = np.linspace(ymin, ymax, nrows)[:-1]
	xv, yv = np.meshgrid(x, y)

	# import matplotlib.pyplot as plt
	# fig, ax = plt.subplots()
	# cs = ax.contourf(xv , yv , f_file)
	# cbar = fig.colorbar(cs)
	# plt.show()

	noise_model = RegularGridInterpolator((y, x), f_file)

	return noise_model, xv, yv, f_file

	# sta_y = 40
	# sta_x = 15
	# sta_loc = np.array([sta_y,sta_x])

	# print(noise_model(sta_loc)[0])
