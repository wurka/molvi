from .models import Cluster, Atom, ClusterAtom
from scipy import optimize
import numpy as np


def shift_atoms(cluster: Cluster, r1: tuple, r2: tuple, r3: tuple, r1prime: tuple, r2prime: tuple, r3prime: tuple):
	"""
	Подвинуть класте так, чтобы конфигурация осталась как прежде
	:param cluster: тот самый атом
	:param r1: координаты точки 1 до перемещения
	:param r2: координаты точки 2 до перемещения
	:param r3: координаты точки 3 до перемещения
	:param r1prime: координаты точки 1 после перемещения
	:param r2prime: координаты точки 2 после перемещения
	:param r3prime: координаты точки 3 после перемещения
	:return: None
	"""
	x1, y1, z1 = r1
	x2, y2, z2 = r2
	x3, y3, z3 = r3
	x1prime, y1prime, z1prime = r1prime
	x2prime, y2prime, z2prime = r2prime
	x3prime, y3prime, z3prime = r3prime

	cluster_atoms = ClusterAtom.objects.filter(cluster=cluster)
	for atom in cluster_atoms:
		xi, yi, zi = atom.atom.x, atom.atom.y, atom.atom.z
		d1 = (xi-x1)**2 - (yi-y1)**2 - (zi-z1)**2
		d2 = (xi-x2)**2 - (yi-y2)**2 - (zi-z2)**2
		d3 = (xi-x3)**2 - (yi-y3)**2 - (zi-z3)**2

		def fun(x):
			a1 = (x[0] - x1prime) ** 2 + (x[1] - y1prime) ** 2 + (x[2] - z1prime) ** 2 - d1
			a2 = (x[0] - x2prime) ** 2 + (x[1] - y2prime) ** 2 + (x[2] - z2prime) ** 2 - d2
			a3 = (x[0] - x3prime) ** 2 + (x[1] - y3prime) ** 2 + (x[2] - z3prime) ** 2 - d3
			return [a1, a2, a3]

		solution = optimize.root(fun=fun, x0=np.asarray([xi, yi, zi], dtype=np.float64))
		atom.atom.x, atom.atom.y, atom.atom.z = solution
		# atom.save()
