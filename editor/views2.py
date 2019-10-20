from .models import Cluster, Atom, ClusterAtom
from scipy import optimize
import numpy as np
from math import sqrt
from .models import Document, Cluster, ClusterAtom
from django.http import HttpResponse
from datetime import datetime


def get_normal(p1: tuple, p2: tuple, p3: tuple):
	"""
	вычислить вектор нормали к плоскости, проходящей через 3 точки
	:param p1: (x1, y1, z1)угол
	:param p2: (x2, y2, z2)
	:param p3: (x3, y3, z3)
	:return: (xn, yn, zn)
	"""
	x1, y1, z1, x2, y2, z2, x3, y3, z3 = p1 + p2 + p3

	ax = x1 - x2
	ay = y1 - y2
	az = z1 - z2
	bx = x2 - x3
	by = y2 - y3
	bz = z2 - z3
	xn, yn, zn = ay*bz - by*az, bx*az - ax*bz, ax*by - bx*ay
	return (xn, yn, zn)

def cosangle_between(v1: tuple, v2: tuple):
	"""
	вычислить угол между 2 векторами
	:param v1: (v1x, v1y, v1z)
	:param v2: (v2x, v2y, v2z)
	:return: косинус угла между векторами
	"""
	v1x, v1y, v1z, v2x, v2y, v2z = v1 + v2
	norm1 = sqrt(v1x**2 + v1y**2 + v1z**2)
	norm2 = sqrt(v2x**2 + v2y**2 + v2z**2)
	multipy = v1x*v2x + v1y*v2y + v1z*v2z
	cosphi = multipy / norm1 / norm2
	return cosphi


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
		d1 = (xi-x1)**2 + (yi-y1)**2 + (zi-z1)**2
		d2 = (xi-x2)**2 + (yi-y2)**2 + (zi-z2)**2
		d3 = (xi-x3)**2 + (yi-y3)**2 + (zi-z3)**2

		if abs(d1) < 0.1 or abs(d2) < 0.1 or abs(d3) < 0.1:
			continue

		normal = get_normal(r1, r2, r3)
		ri2 = ((xi - x2), (yi - y2), (zi - z2))
		ri3 = ((xi - x3), (yi - y3), (zi - z3))
		cosangle1 = cosangle_between(normal, ri2)
		cosangle2 = cosangle_between(normal, ri3)

		normal_prime = get_normal(r1prime, r2prime, r3prime)

		def fun(x):
			a1 = (x[0] - x1prime) ** 2 + (x[1] - y1prime) ** 2 + (x[2] - z1prime) ** 2 - d1
			# a2 = (x[0] - x2prime) ** 2 + (x[1] - y2prime) ** 2 + (x[2] - z2prime) ** 2 - d2
			# a3 = (x[0] - x3prime) ** 2 + (x[1] - y3prime) ** 2 + (x[2] - z3prime) ** 2 - d3
			ri2prime = ((x[0] - x2prime), (x[1] - y2prime), (x[2] - z2prime))
			ri3prime = ((x[0] - x3prime), (x[1] - y3prime), (x[2] - z3prime))
			a2 = cosangle_between(normal_prime, ri2prime) - cosangle1
			a3 = cosangle_between(normal_prime, ri3prime) - cosangle2

			return [a1, a2, a3]

		solution = optimize.root(fun=fun, x0=np.asarray([xi, yi, zi], dtype=np.float64))
		newx, newy, newz = solution.x
		newd1 = (newx-x1prime)**2 + (newy-y1prime)**2 + (newz-z1prime)**2
		newd2 = (newx-x2prime)**2 + (newy-y2prime)**2 + (newz-z2prime)**2
		newd3 = (newx-x3prime)**2 + (newy-y3prime)**2 + (newz-z3prime)**2


		atom.atom.x, atom.atom.y, atom.atom.z = solution.x
		atom.atom.save()


def save_atoms_to_file(request):

	flags = "a"
	if "clear" in request.GET:
		if request.GET["clear"].lower()=="true":
			flags = "w+"

	try:
		adoc = Document.objects.get(is_active=True)

	except Document.DoesNotExists:
		return HttpResponse("There is no active document", status=500)

	clusters = Cluster.objects.filter(document=adoc)

	coordinates = list()
	for cluster in clusters:
		cluster_atoms = ClusterAtom.objects.filter(cluster=cluster)
		for catom in cluster_atoms:
			coordinates.append(str(catom.atom.x))
			coordinates.append(str(catom.atom.y))
			coordinates.append(str(catom.atom.z))

	try:
		with open("/home/wurka/debug/atoms.txt", flags) as file:
			file.write("\t".join(coordinates) + "\r\n")
	except Exception as ex:
		return HttpResponse(str(ex))

	return HttpResponse("Done " + str(datetime.now()))
