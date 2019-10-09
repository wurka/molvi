from django.test import TestCase
from scipy import optimize
import numpy as np


# Create your tests here.
def function_u(x):
    return np.sin(x)


x0 = np.ndarray([1], dtype=np.float64)
x = optimize.minimize(function_u, x0, method="CG")
print(x)
print(">>>>>>>>>")
print(f"{x.x}")
