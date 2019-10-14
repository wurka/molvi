from scipy import optimize


def fun(x):
	a1 = x[0] ** 2 + x[1] ** 2 + x[2] ** 2 - 0
	a2 = x[0] ** 2 + x[1] ** 2 + x[2] ** 2 - 0
	a3 = x[0] ** 2 + x[1] ** 2 + x[2] ** 2 - 0
	return [a1, a2, a3]


x0 = [1, 1, 1]
sol = optimize.root(fun, x0, method='anderson')
print(sol)
