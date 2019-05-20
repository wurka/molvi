# оптимизация энергии молекулы
import numpy as np
import math


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


class Atom:
	def __init__(self, x=0, y=0, z=0, mentab_index=0, name='H', valency=1):
		self.x = x
		self.y = y
		self.z = z
		self.mentab_index = mentab_index
		self.name = name
		self.valency = 1


def calc_bo_(i, j):  # r - расстояние между атомами, i, j - индексы элементов в таблице Менделеева
	r = (atoms[i].x - atoms[j].x) ** 2 + (atoms[i].y - atoms[j].y) ** 2 + (atoms[i].z - atoms[j].z) ** 2
	r = math.sqrt(r)

	if i == j:
		r0 = r_0[i]
	else:
		r0 = 0.5 * (r_0[i] + r_0[j])

	pb01 = pb0_1[atoms[i].mentab_index, atoms[j].mentab_index]
	pb02 = pb0_2[atoms[i].mentab_index, atoms[j].mentab_index]
	pb03 = pb0_3[atoms[i].mentab_index, atoms[j].mentab_index]
	pb04 = pb0_4[atoms[i].mentab_index, atoms[j].mentab_index]
	pb05 = pb0_5[atoms[i].mentab_index, atoms[j].mentab_index]
	pb06 = pb0_6[atoms[i].mentab_index, atoms[j].mentab_index]

	if r0 == 0:
		r0 = r0

	ans = np.exp(pb01 * (r / r0)**pb02)
	ans += np.exp(pb03 * (r / r0)**pb04)
	ans += np.exp(pb05 * (r / r0)**pb06)
	return ans


def get_bond_energy():
	global atoms
	# расчёт всех значений BO`_ij
	n = len(atoms)
	bo_ = np.zeros((n, n), dtype=np.float32)
	for i in range(n):
		for j in range(n):
			bo_[i, j] = calc_bo_(atoms[i].mentab_index, atoms[j].mentab_index)

	# расчёт всех Δ_i
	delta_ = np.zeros(n, dtype=np.float32)
	for i in range(n):
		delta_ = -atoms[i].valency
		for j in range(n):
			delta_[i] += bo_[i, j]

	ans = 0  # энергия Ebond
	for i in range(n):  # цикл по всем атомам
		for j in range(n):
			d_i = delta_[i]
			d_j = delta_[j]
			val_i = atoms[i].valency
			val_j = atoms[j].valency
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

			pbe1 = p_be_1[atoms[i].]
			ans += -d_e[i, j] * boij * math.exp(p_be_1 * (1-boij**pbe1))

	print("bond energy: " + str(ans))

	# E_over energy ###########
	eover = 0
	for i in range(len(atoms)):
		pover = p_over[atoms[i].mentab_index]
		eover += pover * delta_[i] * ( 1/(1 + math.exp(lam_6 * delta_[i])))

	print("E_over energy: " + str(eover))
	ans += eover
	print("total energy: " + str(ans))

	# E_under energy ##########
	eunder = 0 #NEIGHBORS

	return ans


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


# получить полную энергию совокупности атомов
def get_energy():
	e_bond = get_bond_energy()
	# e_over = get_over_energy()
	# e_under = get_under_energy()
	# e_val = get_val_energy()
	# e_pen = get_pen_energy()
	# e_tors = get_tors_energy()
	# e_conj = get_conj_energy()
	# e_vdwaals = get_vdwaals_energy()
	# e_coulomb = get_coulomb_energy()

	return e_bond


if __name__ == "__main__":
	atoms = list()
	atoms.append(Atom(name='H1', x=-1, y=1, mentab_index=0, valency=1))
	atoms.append(Atom(name='H2', x=1, y=1, mentab_index=0, valency=1))
	atoms.append(Atom(name='H3', x=-1, y=-1, mentab_index=0, valency=1))
	atoms.append(Atom(name='C4', x=3, y=0, mentab_index=5, valency=1))
	atoms.append(Atom(name='H5', x=4, y=1, mentab_index=0, valency=1))
	atoms.append(Atom(name='H6', x=2, y=-1, mentab_index=0, valency=1))
	atoms.append(Atom(name='H7', x=4, y=-1, mentab_index=0, valency=1))
	atoms.append(Atom(name='C8', x=0, y=0, mentab_index=5, valency=1))

	print(get_energy())
