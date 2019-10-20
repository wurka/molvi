import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


ax = plt.axes(projection='3d')
colors = ("red", "green", "blue")
sizes = (10, 13, 16)
markers = ["x", "+"]


with open("/home/wurka/debug/atoms.txt", "rt") as file:
	lines = file.readlines()
	for iline, line in enumerate(lines):
		words = line.split("\t")
		x = [float(w) for indx, w in enumerate(words) if indx % 3 == 0]
		y = [float(w) for indx, w in enumerate(words) if indx % 3 == 1]
		z = [float(w) for indx, w in enumerate(words) if indx % 3 == 2]

		ax.plot3D(
			x, y, z, marker=markers[iline % len(markers)], color=colors[iline % len(colors)],
			label='r', markersize=sizes[iline % len(sizes)])

plt.show()

