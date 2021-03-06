# оптимизация энергии молекулы
import numpy as np
import math
from typing import List
from editor.models import Atom, Link, ValenceAngle, ValenceAngleLink, DihedralAngle, DihedralAngleLink
from datetime import datetime
from django.http import HttpResponse
from .models import Document
import json
import io
import matplotlib.pyplot as plt
import base64
from .views import edit_link_set_length


mt_table_size = 110
p_be_1 = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
p_be_1[5, 5] = 0.318  # C-C
p_be_1[5, 0] = -0.454  # C-H
p_be_1[0, 5] = -0.454  # H-C
p_be_1[0, 0] = -0.31  # H-H

d_e = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
d_e[5, 5] = 145.2  # C-C
d_e[5, 0] = 183.8  # C-H
d_e[0, 5] = 183.8  # H-C
d_e[0, 0] = 168.4  # H-H

pb0_1 = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
pb0_1[5, 5] = -0.097  # C-C
pb0_1[5, 0] = -0.013  # C-H
pb0_1[0, 5] = -0.013  # H-C
pb0_1[0, 0] = -0.016  # H-H

pb0_2 = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
pb0_2[5, 5] = 6.38  # C-C
pb0_2[5, 0] = 7.65  # C-H
pb0_2[0, 5] = 7.65  # H-C
pb0_2[0, 0] = 5.98  # H-H

pb0_3 = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
pb0_3[5, 5] = -0.26

pb0_4 = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
pb0_4[5, 5] = 9.37

pb0_5 = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
pb0_5[5, 5] = -0.391

pb0_6 = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
pb0_6[5, 5] = 16.87

r_0 = np.zeros(mt_table_size, dtype=np.float32)
r_0[5] = 1.399
r_0[0] = 0.656

r_0p = np.zeros(mt_table_size, dtype=np.float32)
r_0p[5] = 1.266

r_0pp = np.zeros(mt_table_size, dtype=np.float32)
r_0pp[5] = 1.236

p_over = np.zeros(mt_table_size, dtype=np.float32)
p_over[5] = 52.2
p_over[5] = 117.5

p_under = np.zeros(mt_table_size, dtype=np.float32)
p_under[5] = 29.4

d_e = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
d_e[5, 5] = 145.2
d_e[5, 0] = 183.8
d_e[0, 5] = 183.8
d_e[0, 0] = 168.4

lam_1 = 50.0
lam_2 = 15.61
lam_3 = 5.02
lam_4 = 18.32
lam_5 = 8.32
lam_6 = -8.9
lam_7 = 1.94
lam_8 = -3.47
lam_9 = 5.79
lam_10 = 12.38
lam_11 = 1.49
lam_12 = 1.28
lam_13 = 6.30
lam_14 = 2.72
lam_15 = 33.87
lam_16 = 6.7
lam_17 = 1.06
lam_18 = 2.04
lam_19 = 36.0
lam_20 = 7.98
lam_21 = 0.4
lam_22 = 4.0
lam_23 = 3.17
lam_24 = 10.0
lam_25 = 0.9
lam_26 = -1.14
lam_27 = 2.17
lam_28 = 1.69


class SourceError(Exception):
	def __init__(self, message):
		super(message)
		self.message = message


def calc_bo_(atom1: Atom, atom2: Atom):  # r - расстояние между атомами, i, j - индексы элементов в таблице Менделеева
	i = atom1.mentableindex
	j = atom2.mentableindex

	if r_0[i] == 0:
		raise SourceError("Таблица r_0 не содержит данных для элемента (таблица Менделеева) №{}".format(i))
	if r_0[j] == 0:
		raise SourceError("Таблица r_0 не содержит данных для элемента (таблица Менделеева) №{}".format(j))

	r = (atom1.x - atom2.x) ** 2 + (atom1.y - atom2.y) ** 2 + (atom1.z - atom2.z) ** 2
	r = math.sqrt(r)

	if i == j:
		r0 = r_0[i]
	else:
		r0 = 0.5 * (r_0[i] + r_0[j])

	pb01 = pb0_1[atom1.mentableindex, atom2.mentableindex]
	pb02 = pb0_2[atom1.mentableindex, atom2.mentableindex]
	pb03 = pb0_3[atom1.mentableindex, atom2.mentableindex]
	pb04 = pb0_4[atom1.mentableindex, atom2.mentableindex]
	pb05 = pb0_5[atom1.mentableindex, atom2.mentableindex]
	pb06 = pb0_6[atom1.mentableindex, atom2.mentableindex]

	if r0 == 0:
		r0 = r0

	ans = 0
	if pb02 != 0:
		ans += np.exp(pb01 * (r / r0) ** pb02)
	if pb04 != 0:
		ans += np.exp(pb03 * (r / r0) ** pb04)
	if pb06 != 0:
		ans += np.exp(pb05 * (r / r0) ** pb06)
	return ans


def get_delta(atom: Atom, links: List[Link]):
	"""Рассчёт дельты для атома"""
	delta = 0
	# d_i, цикл по всем связям с atom
	for link in links:
		if link.atom1 == atom:
			atom2 = link.atom2
		elif link.atom2 == atom:
			atom2 = link.atom1
		else:
			continue
		delta += calc_bo_(atom, atom2)

	delta -= atom.valence
	return delta


def get_bond_energy(
		links: List[Link]):
	ebond = 0

	# bond - это энергия связи
	for link in links:  # цикл по всем связям
		d_i = 0
		d_j = 0
		val_i = link.atom1.valence
		val_j = link.atom2.valence
		bo_ij = calc_bo_(link.atom1, link.atom2)

		# d_i, цикл по всем связям с link.atom1
		links2delta = [l for l in links if l != link]
		d_i = get_delta(link.atom1, links2delta)

		# d_j, цикл по всем связям с link.atom2
		d_j = get_delta(link.atom2, links2delta)

		f2 = math.exp(-lam_1 * d_i) + math.exp(-lam_1 * d_j)
		f3 = 1.0/lam_2 * math.log(0.5 * (math.exp(-lam_2 * d_i) + math.exp(-lam_2 * d_j)))
		# if f3 < 0:
		#	f3 = 0  # в оригинале нет такого ограничения
		f1 = (val_i + f2) / (val_i + f2 + f3)
		f1 += (val_j + f2) / (val_j + f2 + f3)
		f1 *= 0.5
		f4 = 1.0 + math.exp(-lam_3 * (lam_4 * bo_ij * bo_ij - d_i) + lam_5)
		f4 = 1.0 / f4
		f5 = 1.0 + math.exp(-lam_3 * (lam_4 * bo_ij * bo_ij - d_j) + lam_5)
		f5 = 1.0 / f5
		boij = bo_ij * f1 * f4 * f5

		pbe1 = p_be_1[link.atom1.mentableindex, link.atom2.mentableindex]
		de = d_e[link.atom1.mentableindex, link.atom2.mentableindex]
		plus = -de * boij * math.exp(pbe1 * (1 - boij ** pbe1))
		if np.isnan(plus):  # скорее всего, не получилось вычислить степень (дробную): boij ** pbe1
			if np.isnan(boij ** pbe1):  # да, так и есть
				plus = 0
				print("Wrong (boij ** pbe1) values. Complex numbers obtained!")
			else:
				print("Some shit happened")
				raise ValueError("see me, fix me!")
		# ebond += plus # uncomment it
		#if (link.atom1.name == 'C' and link.atom2.name == "H") or (link.atom1.name == 'C' and link.atom2.name == "H"):
			return plus
		if link.atom1.name == 'C' and link.atom2.name == "C":
			return plus
		#return ebond  # delete it

	return ebond


"""
for i in range(n):  # цикл по всем атомам
		for j in range(n):
			d_i = delta_[i]
			d_j = delta_[j]
			val_i = atoms[i].valence
			val_j = atoms[j].valence
			bo_ij = bo_[i, j]
			f2 = math.exp(-lam_1 * d_i) + math.exp(-lam_1 * d_j)
			f3 = 0.5*lam_2 * math.log(0.5*(math.exp(-lam_2*d_i) + math.exp(-lam_2*d_j)))
			f1 = (val_i + f2)/(val_i + f2 + f3)
			f1 += (val_j + f2) / (val_j + f2 + f3)
			f1 *= 0.5
			f4 = 1 + math.exp(-lam_3*(lam_4*bo_ij*bo_ij - d_i) + lam_5)
			f4 = 1/f4
			f5 = 1 + math.exp(-lam_3*(lam_4*bo_ij*bo_ij - d_j) + lam_5)
			f5 = 1/f5
			boij = bo_ij*f1*f4*f5

			pbe1 = p_be_1[atoms[i].mentableindex, atoms[j].mentableindex]
			ans += -d_e[i, j] * boij * math.exp(pbe1 * (1-boij**pbe1))

	return ans
	print("bond energy: " + str(ans))

	# E_over energy ###########
	eover = 0
	for i in range(len(atoms)):
		pover = p_over[atoms[i].mentabindex]
		eover += pover * delta_[i] * ( 1/(1 + math.exp(lam_6 * delta_[i])))

	print("E_over energy: " + str(eover))
	ans += eover
	print("total energy: " + str(ans))

	# E_under energy ##########
	# for aindx, atom in enumerate(atoms):

	return ans
	"""


def get_over_energy():
	global atoms
	ans = 0


def get_under_energy():
	raise NotImplementedError("get_under_energy")


def get_val_energy():
	raise NotImplementedError("get_val_energy")


def get_pen_energy():
	raise NotImplementedError("get_pen_energy")


def get_tors_energy():
	raise NotImplementedError("get_tors_energy")


def get_conj_energy():
	raise NotImplementedError("get_conj_energy")


def get_vdwaals_energy():
	raise NotImplementedError("get_vdwaals_energy")


def get_coulomb_energy():
	raise NotImplementedError("get_coulomb_energy")


def get_optimise_sources(request):
	active_doc = Document.objects.get(is_active=True)
	ans = list()

	links = Link.objects.filter(document=active_doc)
	for link in links:
		name1 = link.atom1.name
		name2 = link.atom2.name

		ans.append({
			"selected": True,
			"type": 'link',
			"id": link.id,
			"label": f"{name1}{name2}: ({name1}{link.atom1.documentindex}-{name2}{link.atom2.documentindex})"
		})

	ans = json.dumps(ans)
	return HttpResponse(ans)


def optimize(request):
	f = 3e12  # частота, Гц

	return HttpResponse("OK")


def optimize_legacy(request):
	need_to_step = True
	for x in ["from", "to", "step", "links2stretch"]:
		if x not in request.GET:
			need_to_step = False

	if need_to_step:
		val = float(request.GET["from"])
		to = float(request.GET["to"])
		step = float(request.GET["step"])
		links2stretch = json.loads(request.GET["links2stretch"])

		xvals = list()
		yvals = list()

		while val <= to:
			# применение значений
			stretched_links = [Link.objects.get(id=x) for x in links2stretch]

			class Dummy: pass  # класс для формирования временного расчёта

			# изменение длинн связей
			for slink in stretched_links:
				temp_request = Dummy()
				temp_request.GET = {
					"link": slink.id,
					"length": val
				}

				edit_link_set_length(temp_request)

			active_doc = Document.objects.get(is_active=True)

			atoms = Atom.objects.filter(document=active_doc)
			links = Link.objects.filter(document=active_doc)
			valence_angles = ValenceAngle.objects.filter(document=active_doc)
			dihedral_angles = DihedralAngle.objects.filter(document=active_doc)

			try:
				e = get_bond_energy(links)
			except SourceError as e:
				ans = "Error while optimize: " + e.message
				return HttpResponse(ans, status=500)

			# ans = f"atoms: {len(atoms)}"
			ans = f"bond energy: {e}"
			print(f"Done for length: {val}")

			xvals.append(val)
			yvals.append(e)

			val += step

		plt.clf()
		plt.grid(color='gray', linestyle='--', linewidth=1)
		axes = plt.gca()
		# axes.set_ylim([-180, 0])
		plt.plot(xvals, yvals, marker='x')

		buf = io.BytesIO()
		plt.savefig(buf, format='png')
		buf.seek(0)
		file_bytes = base64.b64encode(buf.getvalue())
		return HttpResponse(file_bytes.decode('utf8'), content_type="image/png")

	return HttpResponse("Oooops")


def debug(request):
	print("you gona fun? ok...")
	atoms = list()
	atoms.append(Atom(name='H1', x=-1, y=1, mentabindex=0, valency=1))
	atoms.append(Atom(name='H2', x=1, y=1, mentabindex=0, valency=1))
	atoms.append(Atom(name='H3', x=-1, y=-1, mentabindex=0, valency=1))
	atoms.append(Atom(name='C4', x=3, y=0, mentabindex=5, valency=1))
	atoms.append(Atom(name='H5', x=4, y=1, mentabindex=0, valency=1))
	atoms.append(Atom(name='H6', x=2, y=-1, mentabindex=0, valency=1))
	atoms.append(Atom(name='H7', x=4, y=-1, mentabindex=0, valency=1))
	atoms.append(Atom(name='C8', x=0, y=0, mentabindex=5, valency=1))

	links = list()
	valenceAngles = list()
	valenceAnglesLinks = list()
	dihedralAngles = list()
	dihedralAnglesLinks = list()

	e = get_bond_energy(
		atoms,
		links,
		valenceAngles,
		valenceAnglesLinks,
		dihedralAngles,
		dihedralAnglesLinks)
	ans = f"Total energy is: {e}"

	return HttpResponse(str(datetime.now()) + "<br>" + ans)
