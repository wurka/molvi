import matplotlib.pyplot as plt
from math import sin
from numpy import sinc
import math

n = 201
start = -0.999
stop = 0.999
x = [start + (stop-start)*i/(n-1) - 0 for i in range(n)]
y = [sinc(x1) for x1 in x]
#y = [-1.0/math.sqrt(1-x1**2) if abs(1-x1**2) > 0.001 else -10 for x1 in x]
y = [math.acos(x1) for x1 in x]
phi0 = math.pi * 1.0/10000.0
y = [math.sin(math.acos(x1) + phi0)/(-math.sqrt(1-x1**2)) for x1 in x]

print(x)
plt.plot(x, y)
plt.show()
