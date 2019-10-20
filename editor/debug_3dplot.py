# from django.test import TestCase
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
ax = plt.axes(projection='3d')
from sympy import Plane, Point3D
from math import acos, sqrt

def array2axis(data):
    x = [data[i] for i in range(len(data)) if i % 3 == 0]
    y = [data[i] for i in range(len(data)) if i % 3 == 1]
    z = [data[i] for i in range(len(data)) if i % 3 == 2]
    return x,y,z


data = [-2.0, 0.0, 0.0, -2.0, 0.0, 0.9667, -1.0789680000000001, 0.0, 1.260136, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9667, 0.921032, 0.0, 1.260136]

data2 = [-1.9785519865712555, -0.08682827970580859, 0.3393251905012485, -2.0, 0.0, 0.9667, -1.0789680000000001, 0.0, 1.260136, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9667, 0.921032, 0.0, 1.260136]


x = [data[i] for i in range(len(data)) if i % 3 == 0]
y = [data[i] for i in range(len(data)) if i % 3 == 1]
z = [data[i] for i in range(len(data)) if i % 3 == 2]

x2 = [data2[i] for i in range(len(data2)) if i % 3 == 0]
y2 = [data2[i] for i in range(len(data2)) if i % 3 == 1]
z2 = [data2[i] for i in range(len(data2)) if i % 3 == 2]


ax.plot3D(x, y, z, marker="o", color='red', label='r', markersize=10)
ax.plot3D(x2, y2, z2, marker='+', color='green', label='r prime', markersize=15)

atomis = ((-2.0, 0.0, 0.0),)
for atomi in atomis:
    xi, yi, zi = atomi
    ax.plot3D((xi,),(yi,),(zi,), marker='x', color='blue', markersize=15)

newatomis = [[-1.95286053, -0.23244826,  0.12018029]]
for newatomi in newatomis:
    x, y, z = newatomi
    ax.plot3D((x,),(y,),(z,), marker='x', color='red', markersize=16)

molecul = [-2.0, 0.0, 0.0, -2.0, 0.0, 0.9667, -1.0789680000000001, 0.0, 1.260136]
mx, my, mz = array2axis(molecul)
ax.plot3D(mx, my, mz, marker='o', color='black')

plt.show()
