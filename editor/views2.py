from .models import Cluster, Atom, ClusterAtom
from scipy import optimize
import numpy as np
from math import sqrt
from .models import Document, Cluster, ClusterAtom, Atom, Link
from .models import DihedralAngle, DihedralAngleLink
from django.http import HttpResponse
from datetime import datetime


def post_with_parameters(*args):
	def decor(method):
		def response(request):
			if request.method != "POST":
				return HttpResponse(f"please use POST request, not {request.method}", status=500)
			for param in args:
				if param not in request.POST:
					return HttpResponse(f"there is no parameter {param}", status=500)
			return method(request)
		return response
	return decor


def get_distance(p1: tuple, p2: tuple):
	"""
	Вычислить расстояние между точками
	:param p1: x1, y1, z1 - координаты точки 1
	:param p2: x2, y2, z2 - координаты точки 2
	:return: distance
	"""
	if isinstance(p1, Atom):
		x1, y1, z1 = p1.x, p1.y, p1.z
	else:
		x1, y1, z1 = p1[0], p1[1], p1[2]
	if isinstance(p2, Atom):
		x2, y2, z2 = p2.x, p2.y, p2.z
	else:
		x2, y2, z2 = p2[0], p2[1], p2[2]

	return sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)


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
	return xn, yn, zn


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


@post_with_parameters("name", "details", "creator")
def save_active_doc(request):
	"""
	Сохранить текущий документ под именем request.POST['name']
	:param request:
	:return: HttpResponse("OK", status=200), елси ОК. HttpResponse("error message", status=500) в случае ошибки
	"""
	try:
		adoc = Document.objects.get(is_active=True)
	except Document.DoesNotExist:
		return HttpResponse("There is no active document", status=500)

	newdoc = Document.objects.create(
		is_active=False, creator=request.POST["creator"],
		details=request.POST['details'], name=request.POST['name'])

	old2new_atoms = dict()  # key - старый атом, value - новый атом

	# кластеры из документа
	clusters = Cluster.objects.filter(document=adoc)
	for cluster in clusters:
		newcluster = Cluster.objects.create(
			document=newdoc,
			caption=adoc.caption
		)
		# атомы
		atoms = ClusterAtom.objects.filter(cluster=cluster)
		for atom in atoms:
			newatom = Atom.objects.create(
				document=newdoc,
				x=atom.x,
				y=atom.y,
				z=atom.z,
				name=atom.name,
				color=atom.color,
				mass=atom.mass,
				radius=atom.radius,
				molfile=atom.molfile,
				molfileindex=atom.molfileindex,
				documentindex=atom.documentindex,
				mentableindex=atom.mentableindex,
				valence=atom.valence
			)
			old2new_atoms[atom.id] = newatom.id
			ClusterAtom.objects.create(
				atom=newatom,
				cluster=newcluster
			)

		# связи
		old2new_links = dict()
		links = Link.objects.filter(document=adoc)
		for link in links:
			newlink = Link.objects.create(
				document=newdoc,
				atom1=Atom.objects.get(id=old2new_atoms[link.atom1.id]),
				atom2=Atom.objects.get(id=old2new_atoms[link.atom2.id])
			)
			old2new_links[link.id] = newlink.id

		# двугранные углы
		dh_angles = DihedralAngle.objects.filter(document=adoc)
		for dh_angle in dh_angles:
			new_dh_angle = DihedralAngle.objects.create(
				name=dh_angle.name,
				document=newdoc
			)
			dh_angle_links = DihedralAngleLink.objects.filter(angle=dh_angle)
			for dh_angle_link in dh_angle_links:
				DihedralAngleLink.objects.create(
					angle=new_dh_angle,
					link=Link.objects.get(id=old2new_links[dh_angle_link.link.id])
				)

	return HttpResponse("OK")


@post_with_parameters("id")
def load_document(request):
	try:
		adoc = Document.objects.get(is_active=True)
	except Document.DoesNotExist:
		Document.objects.create(
			is_active=True,
			creator="Python code",
			details="automaticaly created at load_document function",
			name="auto document",
		)

	# удаляем все записи, связанные с текущим активным документом
	# двугранные углы
	dh_angles = DihedralAngle.objects.filter(document=adoc)
	for dh_angle in dh_angles:
		DihedralAngleLink.objects.filter(angle=dh_angle).delete()
		dh_angle.delete()

	# связи
	Link.objects.filter(document=adoc).delete()

	# валентные углы
	# TODO: добавить удаление валентных угло

	# атомы
	clusters = Cluster.objects.filter(document=adoc)
	for cluster in clusters:
		cluster_atom = ClusterAtom.objects.filter(cluster=cluster)
		cluster_atom.atom.delete()
		cluster.delete()

	# создаём новые записи #################
	try:
		ldoc = Document.objects.get(id=request.GET['id'])
	except Document.DoesNotExist:
		return HttpResponse(
			"there is no document with id {request.GET['id']} in base", status=500)

	adoc.creator = ldoc.creator
	adoc.details = ldoc.details
	adoc.name = ldoc.name

	# атомы
	old2new_atoms = dict()  # список новых атомов
	atoms = Atom.objects.filter(document=ldoc)
	for atom in atoms:
		newatom = Atom.objects.create(
			document=adoc,
			x=atom.x,
			y=atom.y,
			z=atom.z,
			name=atom.name,
			color=atom.color,
			mass=atom.mass,
			radius=atom.radius,
			molfile=atom.molfile,
			molfileindex=atom.molfileindex,
			documentindex=atom.documentindex,
			mentableindex=atom.mentableindex,
			valence=atom.valence
		)
		old2new_atoms[atom.id] = newatom.id

	# кластеры
	old2new_clusters = dict()
	clusters = Cluster.objects.filter(document=ldoc)
	for cluster in clusters:
		newcluster = cluster.objects.create(
			document=adoc,
			caption=cluster.caption
		)
		old2new_clusters[cluster.id] = newcluster.id

		catoms = ClusterAtom.objects.filter(cluster=cluster)
		for catom in catoms:
			ClusterAtom.objects.create(
				cluster=newcluster,
				atom=Atom.objects.get(id=old2new_atoms[catom.atom.id])
			)

	# связи
	old2new_links = dict()
	links = Link.objects.filter(document=ldoc)
	for link in links:
		newlink = Link.objects.create(
			document=adoc,
			atom1=Atom.objects.get(id=old2new_atoms[link.atom1.id])
		)
		old2new_links[link.id] = newlink.id

	# валентные углы
	# TODO: валентные углы доделать

	# двугранные углы
	dh_angles = DihedralAngle.objects.filter(document=ldoc)
	for dh_angle in dh_angles:
		new_dh_angle = DihedralAngle.objects.create(
			document=adoc,
			name=dh_angle.name
		)

		dha_links = DihedralAngleLink.objects.filter(angle=dh_angle)
		for dha_link in dha_links:
			DihedralAngleLink.objects.create(
				angle=new_dh_angle,
				link=Link.objects.get(id=old2new_links[dha_link.link.id])
			)

	return HttpResponse("OK")