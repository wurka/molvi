# оптимизация энергии молекулы
import numpy as np

atom_config = {
	atoms: [{
		x: 0,
		y: 0,
		z: 0,
		caption: 'H'
	}
	]
}

class NotImplementedException: Exc

class Optimizer:
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

	r_0 = np.zeros((mt_table_size), dtype=np.float32)
	r_0[5] = 1.399
	r_0[0] = 0.656

	r_0p = np.zeros((mt_table_size), dtype=np.float32)
	r_0p[5] = 1.266

	r_0pp = np.zeros((mt_table_size), dtype=np.float32)
	r_0pp[5] = 1.236

	d_e = np.zeros((mt_table_size, mt_table_size), dtype=np.float32)
	d_e[5, 5] = 145.2
	d_e[5, 0] = 183.8
	d_e[0, 5] = 183.8
	d_e[0, 0] = 168.4

	def bo_(r, i, j):  # r - расстояние между атомами, i, j - индексы элементов в таблице Менделеева
		if i == j:
			r0 = r_0[i]
		else:
			r0 = 0.5 * (r_0[i] + r_0[j])
		ans = np.exp(pb0_1[i, j] * (r / r0)**pb0_2[i, j])
		ans += np.exp(pb0_3[i, j] * (r / r0)**pb0_4[i, j])
		ans += np.exp(pb0_5[i, j] * (r / r0)**pb0_6[i, j])
		return ans

	def f1(di, dj, vali, valj):  # vali, valj - валентность атомов i и j соответственно
		return 0.5*

def get_bond_energy(r, i, j):
	ans = - d_e[i, j]
	raise NotImplementedError ("get_bond_energy")

def get_over_energy():
	raise NotImplementedError("get_over_energy")

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
	e_over = get_over_energy()
	e_under = get_under_energy()
	e_val = get_val_energy()
	e_pen = get_pen_energy()
	e_tors = get_tors_energy()
	e_conj = get_conj_energy()
	e_vdwaals = get_vdwaals_energy()
	e_coulomb = get_coulomb_energy()