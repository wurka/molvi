# from django.test import TestCase
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
ax = plt.axes(projection='3d')
from sympy import Plane, Point3D
from math import acos, sqrt


data = [
    0.03667164, -0.57293975, 0.24777301, -0.05062748, -0.06806661, 0.79214704, -1.06395922,
    0.31288135, 1.32721277, -2.0007155, -0.17226318, 0.93802569
]

data = [-0.00429334, -0.46211817,  0.11662185,  0.00520712, -0.05948275,
        0.97894422, -1.07997775,  0.08518725,  1.26517019, -1.99990403,
       -0.04693638,  0.96231296]

x = [data[i] for i in range(len(data)) if i % 3 == 0]
y = [data[i] for i in range(len(data)) if i % 3 == 1]
z = [data[i] for i in range(len(data)) if i % 3 == 2]


p1 = Point3D(x[0], y[0], z[0], evaluate=False)
p2 = Point3D(x[1], y[1], z[1], evaluate=False)
p3 = Point3D(x[2], y[2], z[2], evaluate=False)
p4 = Point3D(x[3], y[3], z[3], evaluate=False)
pln1 = Plane(p1, p2, p3)
pln2 = Plane(p2, p3, p4)

#print(pln1.angle_between(pln2))
#print(float(pln1.angle_between(pln2)))


print("my phi")
n1 = pln1.normal_vector
n2 = pln2.normal_vector

d1 = sqrt(n1[0]**2 + n1[1]**2 + n1[2]**2)
d2 = sqrt(n2[0]**2 + n2[1]**2 + n2[2]**2)

print(f"d1: {d1}")
print(f"d2: {d2}")
xx = (n1[0]*n2[0] + n1[1]*n2[1] + n1[2]*n2[2])/(d1*d2)
xx = min(xx, 1)
xx = max(xx, -1)
print(f"under cos: {(n1[0]*n2[0] + n1[1]*n2[1] + n1[2]*n2[2])/(d1*d2)}")

myphi = acos(xx)
print(myphi)

ax.plot3D(x, y, z)
plt.show()
