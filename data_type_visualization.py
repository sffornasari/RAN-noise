import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection


npz = '../DBs/sens_only/2019/001/BGR.HGZ_2019_001.npz'

res = np.load(npz)
keys = list(res.keys())
# Frequencies
pn = res[keys[0]]
# Hours
hours = keys[1:]

# Create Figure
fig, ax = plt.subplots(figsize=(8,6))
# Rectangles
X = 0
Y = 0
labels = [];ticks = [];bars = []
for hour in hours:
	h_al = int(hour.replace('_',''))
	fmt = '%H_%M'
	d = datetime.strptime(hour, fmt)
	labels.append(d.strftime('%H:%M'))
	ticks.append(X)
	bars.append(Rectangle((X, Y), 90, 72, fill=None, edgecolor='blue'))
	
	X += 45
	Y += 72

colors = plt.cm.rainbow(np.linspace(0, 1, len(keys[1:])))
X = 0
Y = 0
x_new = [];y_new = [];
for i,psd in enumerate(keys[1:]):
	X_new = X + pn/10
	Y_new = Y - res[psd]/10 + 30
	# print(res[psd])
	x_new.append(X_new)
	y_new.append(Y_new)	
	X += 45
	Y += 72

# Create Another Rectangle in Upper Left
rect1 = Rectangle((0, Y-72*3), 90*10, 72*3, facecolor='White', edgecolor='black', zorder=10)
ax.add_patch(rect1)
# Add Lines inside the Rectangle
for x in [30,60,90,870,840,810]:
	ax.plot([x,x],[Y-72*2+7.0,Y-8.0],c='#CCCCCC',zorder=11)
# Add ... 
ax.text(390,Y-82.5,'.',size=20,c='#CCCCCC',zorder=11)
ax.text(440,Y-82.5,'.',size=20,c='#CCCCCC',zorder=11)
ax.text(490,Y-82.5,'.',size=20,c='#CCCCCC',zorder=11)
# Area to Write Values
rect2 = Rectangle((0, Y-72*4), 90*10, 72*2, facecolor='White', edgecolor='black', zorder=10)
ax.add_patch(rect2)
# Add Frequencies
x = 0
for val in pn[:-10]:
	ax.text(x+5,Y-72*3-50.5,"{:.3f}".format(round(val,3)).zfill(7),size=4.5,zorder=11,rotation='90')
	x += 22.5
# Plot Lines to Rectangles
ax.plot([12*90,900],[1800-72,Y-72*2],color='black', linestyle='dotted')
ax.plot([12*90,900],[1800,Y],color='black', linestyle='dotted')

for i,(x,y) in enumerate(zip(x_new,y_new)):
	# print(x,y)
	ax.plot(x[:-1]+4,y[:-1], color=colors[i],zorder=10)
# Add Rectangles
coll=PatchCollection(bars, match_original=True, zorder=10)
ax.add_collection(coll)
# Ticks modified
ticks.append(ticks[-1]+45)
labels.append('23:15')
plt.xticks(ticks, labels, rotation='90')
plt.yticks([])
ax.grid(which='major', color='#CCCCCC', linestyle='--', zorder=0)
plt.ylim([0,Y+1])
plt.xlim([0,X+45+1])
plt.tight_layout()
# plt.show()
plt.savefig('tmp.png',dpi=300)